"""Game router for handling multiple game types."""

import logging
from typing import Any

from fastapi import WebSocket

from config import (
    DUELS_MATCHMAKING_TIMEOUT,
    DUELS_MAX_PLAYERS,
    DUELS_MIN_PLAYERS,
    GAME_TYPE_DUELS,
    GAME_TYPE_HANGMAN,
    MATCHMAKING_TIMEOUT_SECONDS,
    MAX_PLAYERS_PER_GAME,
    MIN_PLAYERS_TO_START,
)
from games.duels.events import DuelsEventProcessor
from games.duels.manager import get_duels_manager
from games.duels.messages import SpellCastMessage
from games.hangman.events import HangmanEventProcessor
from games.hangman.manager import get_hangman_manager
from games.hangman.messages import GuessMessage
from models.messages import (
    ClientMessage,
    JoinedMessage,
    JoinMessage,
    LeaveMessage,
    WaitingMessage,
)
from services.matchmaking import get_matchmaking

logger = logging.getLogger(__name__)


class GameRouter:
    """Routes messages to the appropriate game-specific event processor.

    This class handles routing of incoming WebSocket messages to the appropriate
    game-specific processors, manages player-game associations, and coordinates
    matchmaking operations.
    """

    def __init__(self, handler: "WebSocketHandler"):
        self._handler = handler
        self._player_game_types: dict[str, str] = {}
        self._hangman_processor = HangmanEventProcessor(handler)
        self._duels_processor = DuelsEventProcessor(handler)
        self._matchmaking = get_matchmaking()
        self._setup_game_types()

    def _setup_game_types(self) -> None:
        hangman_manager = get_hangman_manager()
        self._matchmaking.register_game_type(
            game_type=GAME_TYPE_HANGMAN,
            min_players=MIN_PLAYERS_TO_START,
            max_players=MAX_PLAYERS_PER_GAME,
            timeout_seconds=MATCHMAKING_TIMEOUT_SECONDS,
            game_creator=hangman_manager.create_game,
            on_game_start=self._on_hangman_game_start,
            joinable_game_finder=hangman_manager.find_joinable_game,
        )

        duels_manager = get_duels_manager()
        self._matchmaking.register_game_type(
            game_type=GAME_TYPE_DUELS,
            min_players=DUELS_MIN_PLAYERS,
            max_players=DUELS_MAX_PLAYERS,
            timeout_seconds=DUELS_MATCHMAKING_TIMEOUT,
            game_creator=duels_manager.create_game,
            on_game_start=self._on_duels_game_start,
        )

    async def _on_hangman_game_start(self, game) -> None:
        manager = get_hangman_manager()
        manager.start_game(game)
        await self._hangman_processor.on_game_start(game)

    async def _on_duels_game_start(self, game) -> None:
        await self._duels_processor.on_game_start(game)

    async def process(
        self, websocket: WebSocket, data: dict, player_id: str | None
    ) -> dict[str, Any] | None:
        """Process an incoming message and route to appropriate handler.

        Args:
            websocket: The WebSocket connection
            data: Raw message data from the client
            player_id: Optional player ID if already authenticated

        Returns:
            A dict with player_id for join messages, None otherwise
        """
        message = ClientMessage.parse(data)

        if message is None:
            return await self._handle_unparsed_message(websocket, data, player_id)

        if isinstance(message, JoinMessage):
            return await self._handle_join(websocket, message)

        if isinstance(message, LeaveMessage) and player_id:
            await self._handle_leave(player_id)

        return None

    async def _handle_unparsed_message(
        self, websocket: WebSocket, data: dict, player_id: str | None
    ) -> None:
        """Handle game-specific messages like guess and spell_cast."""
        msg_type = data.get("type")

        if not player_id:
            await self._handler.send_error(websocket, "Not authenticated")
            return

        game_type = self._player_game_types.get(player_id, GAME_TYPE_HANGMAN)

        if msg_type == "guess":
            try:
                guess_msg = GuessMessage(**data)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid guess message from player {player_id}: {e}",
                    extra={"player_id": player_id, "data": data},
                )
                await self._handler.send_error(websocket, "Invalid guess format")
                return

            if game_type == GAME_TYPE_HANGMAN:
                await self._hangman_processor.handle_guess(
                    player_id, guess_msg, self._matchmaking
                )

        if msg_type == "spell_cast":
            try:
                spell_msg = SpellCastMessage(**data)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid spell cast message from player {player_id}: {e}",
                    extra={"player_id": player_id, "data": data},
                )
                await self._handler.send_error(websocket, "Invalid spell cast format")
                return

            if game_type == GAME_TYPE_DUELS:
                await self._duels_processor.handle_spell_cast(
                    player_id, spell_msg, self._matchmaking
                )
            return

        await self._handler.send_error(websocket, "Unknown message type")

    async def _handle_join(
        self, websocket: WebSocket, message: JoinMessage
    ) -> dict[str, Any] | None:
        game_type = message.game_type
        game_mode = getattr(message, "game_mode", "pvp")  # Extract mode

        if game_type not in (GAME_TYPE_HANGMAN, GAME_TYPE_DUELS):
            await self._handler.send_error(websocket, f"Unknown game type: {game_type}")
            logger.warning(
                f"Attempted join with unknown game type: {game_type}",
                extra={"game_type": game_type, "player_name": message.player_name},
            )
            return None

        if game_type == GAME_TYPE_HANGMAN:
            player, game, late_join = await self._hangman_processor.handle_join(
                websocket, message.player_name, self._matchmaking
            )
            self._player_game_types[player.id] = game_type

            await self._send_joined_message(websocket, player, game)
            if not game:
                await self._broadcast_waiting_status(player.id, game_type)
        else:  # DUELS
            player = self._duels_processor.create_player(websocket, message.player_name)
            self._player_game_types[player.id] = game_type
            self._handler.register_connection(player.id, websocket)

            # Detect PVE mode
            if game_mode == "pve":
                # Create PVE game immediately (no matchmaking)
                game = await self._duels_processor.create_pve_game(player)
                self._matchmaking._player_games[player.id] = game.id

                await self._send_joined_message(websocket, player, game)

                # Start game immediately
                await self._on_duels_game_start(game)
            else:
                # PVP flow (unchanged)
                await self._send_joined_message(websocket, player, None)

                game = await self._duels_processor.enqueue_and_try_start(
                    player, self._matchmaking
                )

                await self._broadcast_waiting_status(player.id, game_type)

        logger.info(
            f"Player {player.name} joined {game_type} game ({game_mode} mode)",
            extra={
                "player_id": player.id,
                "game_id": game.id if game else None,
                "game_type": game_type,
                "game_mode": game_mode,
                "late_join": late_join if game_type == GAME_TYPE_HANGMAN else False,
            },
        )

        return {"player_id": player.id}

    async def _send_joined_message(self, websocket: WebSocket, player, game) -> None:
        """Send the joined confirmation message to a player."""
        await self._handler.send_to_websocket(
            websocket,
            JoinedMessage(
                player_id=player.id,
                game_id=game.id if game else "",
                player_name=player.name,
            ),
        )

    async def _broadcast_waiting_status(
        self, new_player_id: str, game_type: str
    ) -> None:
        queue_size = self._matchmaking.get_queue_size(game_type)
        waiting_msg = WaitingMessage(
            players_in_queue=queue_size,
            message=f"Esperando jugadores... ({queue_size} en cola)",
        )

        for queued_player in self._matchmaking.get_queued_players(game_type):
            await self._handler.send_to_player(queued_player.id, waiting_msg)

    async def _handle_leave(self, player_id: str) -> None:
        game_type = self._player_game_types.get(player_id, GAME_TYPE_HANGMAN)

        self._matchmaking.remove_player(player_id)
        self._matchmaking.remove_player_from_game(player_id)

        if game_type == GAME_TYPE_HANGMAN:
            await self._hangman_processor.handle_leave(player_id, self._matchmaking)
        elif game_type == GAME_TYPE_DUELS:
            await self._duels_processor.handle_leave(player_id, self._matchmaking)

        self._player_game_types.pop(player_id, None)

        logger.info(
            "Player left game", extra={"player_id": player_id, "game_type": game_type}
        )
