"""Game models for the maze-hangman game."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from fastapi import WebSocket


class GameStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Station:
    """Represents a player's current station state."""
    word: str
    guessed_letters: set[str] = field(default_factory=set)
    attempts_left: int = 6

    @property
    def revealed(self) -> str:
        """Return the word with unguessed letters as underscores."""
        return " ".join(
            letter if letter.upper() in self.guessed_letters else "_"
            for letter in self.word
        )

    @property
    def is_complete(self) -> bool:
        """Check if the word has been fully guessed."""
        return all(letter.upper() in self.guessed_letters for letter in self.word)

    @property
    def is_failed(self) -> bool:
        """Check if the player has run out of attempts."""
        return self.attempts_left <= 0

    def guess(self, letter: str) -> bool:
        """
        Process a letter guess.
        Returns True if the letter is in the word, False otherwise.
        """
        letter = letter.upper()
        if letter in self.guessed_letters:
            return True  # Already guessed, no penalty

        self.guessed_letters.add(letter)

        if letter in self.word.upper():
            return True
        else:
            self.attempts_left -= 1
            return False


@dataclass
class Player:
    """Represents a player in the game."""
    id: str
    name: str
    websocket: "WebSocket"
    current_station: int = 1
    station_state: Station | None = None
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
class Game:
    """Represents a game session."""
    id: str
    words: list[str]
    status: GameStatus = GameStatus.WAITING
    players: dict[str, Player] = field(default_factory=dict)
    winner: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, words: list[str]) -> "Game":
        """Create a new game with the given words."""
        game_id = str(uuid.uuid4())[:8].upper()
        return cls(id=game_id, words=words)

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
