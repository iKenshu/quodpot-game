"""Base models for shared game functionality."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from fastapi import WebSocket


class GameStatus(str, Enum):
    """Status of a game."""
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Player:
    """Base class for a player in any game."""
    id: str
    name: str
    websocket: "WebSocket"
    connected: bool = True

    @classmethod
    def create(cls, name: str, websocket: "WebSocket") -> "Player":
        """Create a new player with a unique ID."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            websocket=websocket,
        )


@dataclass
class BaseGame:
    """Base class for all game types."""
    id: str
    game_type: str
    status: GameStatus = GameStatus.WAITING
    players: dict[str, Player] = field(default_factory=dict)
    winner: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def generate_id(cls) -> str:
        """Generate a unique game ID."""
        return str(uuid.uuid4())[:8].upper()

    def add_player(self, player: Player) -> None:
        """Add a player to the game."""
        self.players[player.id] = player

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the game."""
        if player_id in self.players:
            self.players[player_id].connected = False

    def get_player(self, player_id: str) -> Player | None:
        """Get a player by ID."""
        return self.players.get(player_id)

    @property
    def connected_players(self) -> list[Player]:
        """Get all connected players."""
        return [p for p in self.players.values() if p.connected]

    @property
    def player_count(self) -> int:
        """Get the number of connected players."""
        return len(self.connected_players)
