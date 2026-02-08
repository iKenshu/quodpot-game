"""Duels game manager."""

from config import DUELS_ROUNDS_TO_WIN
from models.base import GameStatus, Player
from models.player_wrapper import HumanPlayerWrapper
from .models import DuelGame, RoundResult, Spell


class DuelsManager:
    def __init__(self):
        self._games: dict[str, DuelGame] = {}

    def create_game(self) -> DuelGame:
        game = DuelGame(
            id=DuelGame.generate_id(),
            game_type="duels",
            rounds_to_win=DUELS_ROUNDS_TO_WIN,
        )
        self._games[game.id] = game
        return game

    def get_game(self, game_id: str) -> DuelGame | None:
        return self._games.get(game_id)

    def remove_game(self, game_id: str) -> None:
        if game_id in self._games:
            del self._games[game_id]

    def create_pve_game(self, human_player: Player, ai_service) -> DuelGame:
        """Create a PVE game with AI opponent."""
        game = DuelGame(
            id=DuelGame.generate_id(),
            game_type="duels",
            rounds_to_win=DUELS_ROUNDS_TO_WIN,
            game_mode="pve",
        )

        game.add_player(human_player)

        ai_wrapper = ai_service.create_ai_player(game.id)

        ai_player = Player(
            id=ai_wrapper.id,
            name=ai_wrapper.name,
            websocket=None,  # type: ignore
            connected=True,
        )
        game.add_player(ai_player)

        game.player_wrappers[human_player.id] = HumanPlayerWrapper(
            player=human_player,
            websocket=human_player.websocket
        )
        game.player_wrappers[ai_wrapper.id] = ai_wrapper

        self._games[game.id] = game
        return game

    def start_game(self, game: DuelGame) -> None:
        game.status = GameStatus.PLAYING
        players = list(game.players.values())
        if len(players) != 2:
            raise ValueError(f"Duels requires exactly 2 players, got {len(players)}")

        game.player1_id = players[0].id
        game.player2_id = players[1].id

    def process_spell_cast(
        self, game: DuelGame, player_id: str, spell: Spell
    ) -> tuple[bool, RoundResult | None]:
        round_complete = game.process_spell_cast(player_id, spell)

        if not round_complete:
            return False, None

        result = game.resolve_current_round()
        return True, result

    @property
    def active_games(self) -> list[DuelGame]:
        return [
            game for game in self._games.values() if game.status != GameStatus.FINISHED
        ]


_duels_manager: DuelsManager | None = None


def get_duels_manager() -> DuelsManager:
    global _duels_manager
    if _duels_manager is None:
        _duels_manager = DuelsManager()
    return _duels_manager
