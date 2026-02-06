from dataclasses import dataclass, field

from fastapi import WebSocket

from ...models.base import BaseGame, GameStatus, Player


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
class HangmanPlayer(Player):
    """Hangman-specific player with station tracking."""

    current_station: int = 1
    station_state: Station | None = None

    @classmethod
    def create(cls, name: str, websocket: "WebSocket") -> "HangmanPlayer":
        """Create a new Hangman player."""
        player = Player.create(name, websocket)
        return cls(
            id=player.id,
            name=player.name,
            websocket=player.websocket,
            connected=player.connected,
        )


@dataclass
class HangmanGame(BaseGame):
    """Hangman game with words and stations."""

    words: list[str] = field(default_factory=list)

    def __init__(self, id: str, words: list[str]):
        super().__init__(id=id, game_type="hangman")
        self.words = words

    @classmethod
    def create(cls, words: list[str]) -> "HangmanGame":
        """Create a new Hangman game with the given words."""
        game_id = cls.generate_id()
        return cls(id=game_id, words=words)
