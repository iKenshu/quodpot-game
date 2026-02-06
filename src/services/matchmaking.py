"""Matchmaking service for player queue management."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Awaitable

from ..models.game import Player, Game
from ..config import MAX_PLAYERS_PER_GAME, MIN_PLAYERS_TO_START, MATCHMAKING_TIMEOUT_SECONDS
from .game_manager import get_game_manager


@dataclass
class QueuedPlayer:
    """A player waiting in the matchmaking queue."""
    player: Player
    joined_at: datetime = field(default_factory=datetime.now)


class Matchmaking:
    """Manages the matchmaking queue and game creation."""

    def __init__(self):
        self._queue: list[QueuedPlayer] = []
        self._player_games: dict[str, str] = {}  # player_id -> game_id
        self._timeout_task: asyncio.Task | None = None
        self._on_game_start: Callable[[Game], Awaitable[None]] | None = None

    def set_game_start_callback(
        self, callback: Callable[[Game], Awaitable[None]]
    ) -> None:
        """Set the callback to be called when a game starts."""
        self._on_game_start = callback

    def try_join_active_game(self, player: Player) -> Game | None:
        """Try to place a player directly into an active game."""
        game_manager = get_game_manager()
        game = game_manager.find_joinable_game()

        if game is None:
            return None

        game_manager.add_player_to_active_game(game, player)
        self._player_games[player.id] = game.id
        return game

    async def add_player(self, player: Player) -> tuple[Game | None, bool]:
        """
        Add a player to an active game or the matchmaking queue.
        Returns (Game, True) if late-joined an active game,
        (Game, False) if game started from queue,
        (None, False) if waiting in queue.
        """
        # Check if player is already in queue or game
        if any(qp.player.id == player.id for qp in self._queue):
            return None, False

        game = self.try_join_active_game(player)
        if game is not None:
            return game, True

        queued = QueuedPlayer(player=player)
        self._queue.append(queued)

        # Start timeout task if this is the first player
        if len(self._queue) == MIN_PLAYERS_TO_START and self._timeout_task is None:
            self._timeout_task = asyncio.create_task(self._timeout_start())

        # Check if we have enough players to start
        if len(self._queue) >= MAX_PLAYERS_PER_GAME:
            game = await self._start_game()
            return game, False

        return None, False

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the queue."""
        self._queue = [qp for qp in self._queue if qp.player.id != player_id]

        # Cancel timeout if queue is empty
        if len(self._queue) < MIN_PLAYERS_TO_START and self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

    async def _timeout_start(self) -> None:
        """Start the game after a timeout if we have minimum players."""
        try:
            await asyncio.sleep(MATCHMAKING_TIMEOUT_SECONDS)
            if len(self._queue) >= MIN_PLAYERS_TO_START:
                await self._start_game()
        except asyncio.CancelledError:
            pass

    async def _start_game(self) -> Game:
        """Create and start a game with queued players."""
        # Cancel timeout task
        if self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

        # Take players from queue (up to max)
        players_to_start = self._queue[:MAX_PLAYERS_PER_GAME]
        self._queue = self._queue[MAX_PLAYERS_PER_GAME:]

        # Create game
        game_manager = get_game_manager()
        game = game_manager.create_game()

        # Add players to game
        for queued in players_to_start:
            game.add_player(queued.player)
            self._player_games[queued.player.id] = game.id

        # Start the game
        game_manager.start_game(game)

        # Notify via callback
        if self._on_game_start:
            await self._on_game_start(game)

        return game

    def get_player_game(self, player_id: str) -> str | None:
        """Get the game ID for a player."""
        return self._player_games.get(player_id)

    def remove_player_from_game(self, player_id: str) -> None:
        """Remove a player's game association."""
        if player_id in self._player_games:
            del self._player_games[player_id]

    @property
    def queue_size(self) -> int:
        """Get the current queue size."""
        return len(self._queue)

    @property
    def queued_players(self) -> list[Player]:
        """Get all players in the queue."""
        return [qp.player for qp in self._queue]


# Global singleton instance
_matchmaking: Matchmaking | None = None


def get_matchmaking() -> Matchmaking:
    """Get the global matchmaking instance."""
    global _matchmaking
    if _matchmaking is None:
        _matchmaking = Matchmaking()
    return _matchmaking
