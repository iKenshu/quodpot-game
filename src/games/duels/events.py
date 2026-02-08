"""Duels event processor."""

import asyncio
import logging

from fastapi import WebSocket

from models.base import GameStatus, Player
from models.messages import ErrorMessage
from models.player_wrapper import AIPlayerWrapper, HumanPlayerWrapper

from .manager import get_duels_manager
from .messages import (
    DuelOverMessage,
    DuelStartMessage,
    OpponentCastMessage,
    RoundResultMessage,
    RoundStartMessage,
    SpellCastMessage,
)
from .models import DuelGame, RoundResult, Spell
from .pve_service import PVEService

logger = logging.getLogger(__name__)


class DuelsEventProcessor:
    def __init__(self, handler, pve_service: PVEService | None = None):
        self._handler = handler
        self._pve_service = pve_service or PVEService()

    def create_player(self, websocket: WebSocket, player_name: str) -> Player:
        return Player.create(player_name, websocket)

    async def enqueue_and_try_start(
        self, player: Player, matchmaking
    ) -> DuelGame | None:
        matchmaking.enqueue_player(player, "duels")
        return await matchmaking.try_start_game("duels")

    async def create_pve_game(self, player: Player) -> DuelGame:
        """Create and start a PVE game immediately."""
        manager = get_duels_manager()
        game = manager.create_pve_game(player, self._pve_service)
        return game

    async def on_game_start(self, game: DuelGame) -> None:
        manager = get_duels_manager()
        manager.start_game(game)

        players = list(game.players.values())
        player1, player2 = players[0], players[1]

        for player_id, player in game.players.items():
            if player_id not in game.player_wrappers:
                websocket = self._handler._connections.get(player_id)
                if websocket:
                    game.player_wrappers[player_id] = HumanPlayerWrapper(
                        player=player, websocket=websocket
                    )

        player1_wrapper = game.player_wrappers.get(player1.id)
        if player1_wrapper:
            await player1_wrapper.send_message(
                DuelStartMessage(
                    opponent_id=player2.id,
                    opponent_name=player2.name,
                    rounds_to_win=game.rounds_to_win,
                )
            )

        player2_wrapper = game.player_wrappers.get(player2.id)
        if player2_wrapper:
            await player2_wrapper.send_message(
                DuelStartMessage(
                    opponent_id=player1.id,
                    opponent_name=player1.name,
                    rounds_to_win=game.rounds_to_win,
                )
            )

        await self._send_round_start(game)

    async def handle_spell_cast(
        self, player_id: str, message: SpellCastMessage, matchmaking
    ) -> None:
        manager = get_duels_manager()

        game_id = matchmaking.get_player_game(player_id)
        if not game_id:
            return

        game = manager.get_game(game_id)
        if not game or game.status != GameStatus.PLAYING:
            return

        try:
            spell = Spell(message.spell)
            round_complete, result = manager.process_spell_cast(game, player_id, spell)

            if not round_complete:
                opponent_id = self._get_opponent_id(game, player_id)
                if opponent_id:
                    opponent_wrapper = game.player_wrappers.get(opponent_id)

                    if isinstance(opponent_wrapper, AIPlayerWrapper):
                        await self._handle_ai_response(game, opponent_id)
                    else:
                        opponent_player = game.player_wrappers.get(opponent_id)
                        if opponent_player:
                            await opponent_player.send_message(OpponentCastMessage())
            else:
                await self._send_round_results(game, result)

                if game.check_game_over():
                    await self._send_game_over(game)
                    game.status = GameStatus.FINISHED
                else:
                    await asyncio.sleep(3)
                    game.start_new_round()
                    await self._send_round_start(game)

        except ValueError as e:
            logger.warning(f"Invalid spell cast: {e}", extra={"player_id": player_id})
            await self._handler.send_to_player(player_id, ErrorMessage(message=str(e)))

    async def _handle_ai_response(self, game: DuelGame, ai_player_id: str) -> None:
        """Handle AI spell cast response."""
        manager = get_duels_manager()
        spell = await self._pve_service.get_ai_spell_choice(game, ai_player_id)
        round_complete, result = manager.process_spell_cast(game, ai_player_id, spell)

        if round_complete:
            await self._send_round_results(game, result)

            if game.check_game_over():
                await self._send_game_over(game)
                game.status = GameStatus.FINISHED
            else:
                await asyncio.sleep(3)
                game.start_new_round()
                await self._send_round_start(game)

    async def _send_round_start(self, game: DuelGame) -> None:
        message = RoundStartMessage(
            round_number=game.current_round.round_number,
        )
        for player_id, wrapper in game.player_wrappers.items():
            await wrapper.send_message(message)

    async def _send_round_results(
        self, game: DuelGame, result: RoundResult | None
    ) -> None:
        if result is None:
            return

        current = game.current_round
        player1 = game.get_player(game.player1_id)
        player2 = game.get_player(game.player2_id)

        if (
            not player1
            or not player2
            or not current.player1_cast
            or not current.player2_cast
        ):
            return

        player1_result = (
            "tie"
            if result == RoundResult.TIE
            else ("win" if result == RoundResult.PLAYER1_WINS else "lose")
        )
        player2_result = (
            "tie"
            if result == RoundResult.TIE
            else ("win" if result == RoundResult.PLAYER2_WINS else "lose")
        )

        player1_wrapper = game.player_wrappers.get(player1.id)
        if player1_wrapper:
            await player1_wrapper.send_message(
                RoundResultMessage(
                    round_number=current.round_number,
                    your_spell=current.player1_cast.spell.value,
                    opponent_spell=current.player2_cast.spell.value,
                    result=player1_result,
                    your_score=game.player1_score,
                    opponent_score=game.player2_score,
                )
            )

        player2_wrapper = game.player_wrappers.get(player2.id)
        if player2_wrapper:
            await player2_wrapper.send_message(
                RoundResultMessage(
                    round_number=current.round_number,
                    your_spell=current.player2_cast.spell.value,
                    opponent_spell=current.player1_cast.spell.value,
                    result=player2_result,
                    your_score=game.player2_score,
                    opponent_score=game.player1_score,
                )
            )

    async def _send_game_over(self, game: DuelGame) -> None:
        winner_id = (
            game.player1_id
            if game.player1_score >= game.rounds_to_win
            else game.player2_id
        )
        loser_id = game.player2_id if winner_id == game.player1_id else game.player1_id

        winner = game.get_player(winner_id)
        loser = game.get_player(loser_id)

        if not winner or not loser:
            return

        winner_score = (
            game.player1_score if winner_id == game.player1_id else game.player2_score
        )
        loser_score = (
            game.player2_score if winner_id == game.player1_id else game.player1_score
        )
        final_score = f"{winner_score}-{loser_score}"

        game.winner = winner_id

        winner_wrapper = game.player_wrappers.get(winner_id)
        if winner_wrapper:
            await winner_wrapper.send_message(
                DuelOverMessage(
                    winner_id=winner_id,
                    winner_name=winner.name,
                    final_score=final_score,
                    your_result="victory",
                )
            )

        loser_wrapper = game.player_wrappers.get(loser_id)
        if loser_wrapper:
            await loser_wrapper.send_message(
                DuelOverMessage(
                    winner_id=winner_id,
                    winner_name=winner.name,
                    final_score=final_score,
                    your_result="defeat",
                )
            )

    async def handle_leave(self, player_id: str, matchmaking) -> None:
        manager = get_duels_manager()

        game_id = matchmaking.get_player_game(player_id)
        if not game_id:
            return

        game = manager.get_game(game_id)
        if not game:
            return

        game.remove_player(player_id)

        if game.status == GameStatus.PLAYING:
            opponent_id = self._get_opponent_id(game, player_id)
            if opponent_id:
                opponent = game.get_player(opponent_id)
                if opponent:
                    game.winner = opponent_id
                    game.status = GameStatus.FINISHED

                    await self._handler.send_to_player(
                        opponent_id,
                        DuelOverMessage(
                            winner_id=opponent_id,
                            winner_name=opponent.name,
                            final_score="Victoria por forfeit",
                            your_result="victory",
                        ),
                    )

    def _get_opponent_id(self, game: DuelGame, player_id: str) -> str | None:
        if player_id == game.player1_id:
            return game.player2_id
        elif player_id == game.player2_id:
            return game.player1_id
        return None
