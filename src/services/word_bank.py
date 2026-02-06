"""Word bank service for loading and selecting game words."""

import random
from pathlib import Path


class WordBank:
    """Manages the pool of words for the hangman game."""

    def __init__(self, words_file: Path | None = None):
        """Initialize the word bank with words from a file."""
        if words_file is None:
            words_file = Path(__file__).parent.parent / "data" / "words.txt"

        self._words: list[str] = []
        self._load_words(words_file)

    def _load_words(self, words_file: Path) -> None:
        """Load words from the file."""
        if not words_file.exists():
            raise FileNotFoundError(f"Words file not found: {words_file}")

        with open(words_file, "r", encoding="utf-8") as f:
            self._words = [
                line.strip().upper()
                for line in f
                if line.strip() and line.strip().isalpha()
            ]

        if len(self._words) < 10:
            raise ValueError("Words file must contain at least 10 words")

    def select_words(self, count: int = 10) -> list[str]:
        """Select random words for a game."""
        if count > len(self._words):
            raise ValueError(
                f"Cannot select {count} words, only {len(self._words)} available"
            )

        return random.sample(self._words, count)

    @property
    def total_words(self) -> int:
        """Get the total number of words available."""
        return len(self._words)


_word_bank: WordBank | None = None


def get_word_bank() -> WordBank:
    """Get the global word bank instance."""
    global _word_bank
    if _word_bank is None:
        _word_bank = WordBank()
    return _word_bank
