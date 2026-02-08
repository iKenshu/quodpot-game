"""Matchmaking service for player queue management with multi-game support."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Awaitable, Callable

from config import (
    MATCHMAKING_TIMEOUT_SECONDS,
    MAX_PLAYERS_PER_GAME,
    MIN_PLAYERS_TO_START,
)
from models.base import BaseGame, GameStatus, Player


@dataclass
class QueuedPlayer:
    """A player waiting in the matchmaking queue."""

    player: Player
    game_type: str
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class GameTypeConfig:
    """Configuration for a specific game type."""

    min_players: int
    max_players: int
    timeout_seconds: int
    game_creator: Callable[[], BaseGame]


class Matchmaking:
    """Manages the matchmaking queue and game creation for multiple game types."""

    def __init__(self):
        self._queues: dict[str, list[QueuedPlayer]] = {}
        self._player_games: dict[str, str] = {}
        self._player_types: dict[str, str] = {}
        self._timeout_tasks: dict[str, asyncio.Task] = {}
        self._callbacks: dict[str, Callable[[BaseGame], Awaitable[None]]] = {}
        self._configs: dict[str, GameTypeConfig] = {}
        self._joinable_game_finders: dict[str, Callable[[], BaseGame | None]] = {}

    def register_game_type(
        self,
        game_type: str,
        min_players: int,
        max_players: int,
        timeout_seconds: int,
        game_creator: Callable[[], BaseGame],
        on_game_start: Callable[[BaseGame], Awaitable[None]],
        joinable_game_finder: Callable[[], BaseGame | None] | None = None,
    ) -> None:
        """Register a new game type with its configuration."""
        self._configs[game_type] = GameTypeConfig(
            min_players=min_players,
            max_players=max_players,
            timeout_seconds=timeout_seconds,
            game_creator=game_creator,
        )
        self._callbacks[game_type] = on_game_start
        self._queues[game_type] = []
        if joinable_game_finder:
            self._joinable_game_finders[game_type] = joinable_game_finder

    def try_join_active_game(self, player: Player, game_type: str) -> BaseGame | None:
        """Try to place a player directly into an active game."""
        finder = self._joinable_game_finders.get(game_type)
        if finder is None:
            return None

        game = finder()
        if game is None:
            return None

        self._player_games[player.id] = game.id
        self._player_types[player.id] = game_type
        return game

    async def add_player(
        self, player: Player, game_type: str
    ) -> tuple[BaseGame | None, bool]:
        """Add a player and automatically start game when conditions are met.

        This is the main method for games like Hangman that support late-joining
        and automatic game start when the queue is full.

        Returns:
            (Game, True) if late-joined an active game,
            (Game, False) if game started from queue,
            (None, False) if waiting in queue.
        """
        if game_type not in self._configs:
            return None, False

        config = self._configs[game_type]
        queue = self._queues[game_type]

        if any(qp.player.id == player.id for qp in queue):
            return None, False

        game = self.try_join_active_game(player, game_type)
        if game is not None:
            return game, True

        queued = QueuedPlayer(player=player, game_type=game_type)
        queue.append(queued)
        self._player_types[player.id] = game_type

        if len(queue) == config.min_players and game_type not in self._timeout_tasks:
            self._timeout_tasks[game_type] = asyncio.create_task(
                self._timeout_start(game_type)
            )

        if len(queue) >= config.max_players:
            game = await self._start_game(game_type)
            return game, False

        return None, False

    def enqueue_player(self, player: Player, game_type: str) -> bool:
        """Add a player to the queue without triggering game start.

        Use this for games like Duels that need manual control over when to
        start the game (e.g., require exactly 2 players, no late-joining).
        Call try_start_game() separately to check if game can start.

        Returns:
            True if player was enqueued, False if already in queue or unknown game type.
        """
        if game_type not in self._configs:
            return False

        queue = self._queues[game_type]
        if any(qp.player.id == player.id for qp in queue):
            return False

        queued = QueuedPlayer(player=player, game_type=game_type)
        queue.append(queued)
        self._player_types[player.id] = game_type
        return True

    async def try_start_game(self, game_type: str) -> BaseGame | None:
        """Check if the queue has enough players and start a game if ready.

        Pairs with enqueue_player() for games that need manual start control.
        Starts game if queue size >= max_players, or after timeout if >= min_players.

        Returns:
            The game if started, None if still waiting for more players.
        """
        if game_type not in self._configs:
            return None

        config = self._configs[game_type]
        queue = self._queues[game_type]

        if len(queue) == config.min_players and game_type not in self._timeout_tasks:
            self._timeout_tasks[game_type] = asyncio.create_task(
                self._timeout_start(game_type)
            )

        if len(queue) >= config.max_players:
            return await self._start_game(game_type)

        return None

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the queue."""
        game_type = self._player_types.get(player_id)
        if not game_type or game_type not in self._queues:
            return

        queue = self._queues[game_type]
        self._queues[game_type] = [qp for qp in queue if qp.player.id != player_id]

        config = self._configs.get(game_type)
        if config and len(self._queues[game_type]) < config.min_players:
            if game_type in self._timeout_tasks:
                self._timeout_tasks[game_type].cancel()
                del self._timeout_tasks[game_type]

        if player_id in self._player_types:
            del self._player_types[player_id]

    async def _timeout_start(self, game_type: str) -> None:
        """Start the game after a timeout if we have minimum players."""
        config = self._configs.get(game_type)
        if not config:
            return

        try:
            await asyncio.sleep(config.timeout_seconds)
            queue = self._queues.get(game_type, [])
            if len(queue) >= config.min_players:
                await self._start_game(game_type)
        except asyncio.CancelledError:
            pass

    async def _start_game(self, game_type: str) -> BaseGame:
        """Create and start a game with queued players."""
        config = self._configs.get(game_type)
        if not config:
            raise ValueError(f"Unknown game type: {game_type}")

        if game_type in self._timeout_tasks:
            self._timeout_tasks[game_type].cancel()
            del self._timeout_tasks[game_type]

        queue = self._queues[game_type]
        players_to_start = queue[: config.max_players]
        self._queues[game_type] = queue[config.max_players :]

        game = config.game_creator()

        for queued in players_to_start:
            game.add_player(queued.player)
            self._player_games[queued.player.id] = game.id

        game.status = GameStatus.PLAYING

        callback = self._callbacks.get(game_type)
        if callback:
            await callback(game)

        return game

    def get_player_game(self, player_id: str) -> str | None:
        """Get the game ID for a player."""
        return self._player_games.get(player_id)

    def get_player_game_type(self, player_id: str) -> str | None:
        """Get the game type for a player."""
        return self._player_types.get(player_id)

    def remove_player_from_game(self, player_id: str) -> None:
        """Remove a player's game association."""
        if player_id in self._player_games:
            del self._player_games[player_id]
        if player_id in self._player_types:
            del self._player_types[player_id]

    def get_queue_size(self, game_type: str) -> int:
        """Get the current queue size for a game type."""
        return len(self._queues.get(game_type, []))

    def get_queued_players(self, game_type: str) -> list[Player]:
        """Get all players in the queue for a game type."""
        queue = self._queues.get(game_type, [])
        return [qp.player for qp in queue]

    @property
    def queue_size(self) -> int:
        """Get the total queue size across all game types (for backward compatibility)."""
        return sum(len(q) for q in self._queues.values())

    @property
    def queued_players(self) -> list[Player]:
        """Get all players in all queues (for backward compatibility)."""
        all_players = []
        for queue in self._queues.values():
            all_players.extend(qp.player for qp in queue)
        return all_players


_matchmaking: Matchmaking | None = None


def get_matchmaking() -> Matchmaking:
    """Get the global matchmaking instance."""
    global _matchmaking
    if _matchmaking is None:
        _matchmaking = Matchmaking()
    return _matchmaking
