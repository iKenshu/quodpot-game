
from ...config import TOTAL_STATIONS, MAX_ATTEMPTS_PER_WORD, MAX_PLAYERS_PER_GAME
from ...services.word_bank import get_word_bank
from ...models.base import GameStatus
from .models import HangmanGame, HangmanPlayer, Station


class HangmanGameManager:
    """Manages Hangman game sessions and logic."""

    def __init__(self):
        self._games: dict[str, HangmanGame] = {}

    def create_game(self) -> HangmanGame:
        """Create a new game with random words."""
        word_bank = get_word_bank()
        words = word_bank.select_words(TOTAL_STATIONS)
        game = HangmanGame.create(words)
        self._games[game.id] = game
        return game

    def get_game(self, game_id: str) -> HangmanGame | None:
        """Get a game by ID."""
        return self._games.get(game_id)

    def remove_game(self, game_id: str) -> None:
        """Remove a game from the manager."""
        if game_id in self._games:
            del self._games[game_id]

    def start_game(self, game: HangmanGame) -> None:
        """Start a game and initialize all players."""
        game.status = GameStatus.PLAYING

        for player in game.players.values():
            self._init_player_station(game, player)

    def _init_player_station(self, game: HangmanGame, player: HangmanPlayer) -> None:
        """Initialize a player's current station."""
        word = game.words[player.current_station - 1]
        player.station_state = Station(
            word=word,
            attempts_left=MAX_ATTEMPTS_PER_WORD
        )

    def process_guess(
        self, game: HangmanGame, player: HangmanPlayer, letter: str
    ) -> dict:
        """
        Process a letter guess from a player.

        Returns a dict with the result:
        {
            "correct": bool,
            "letter": str,
            "revealed": str,
            "attempts_left": int,
            "station_complete": bool,
            "station_failed": bool,
            "game_won": bool,
            "word": str (only if station complete or failed)
        }
        """
        if game.status != GameStatus.PLAYING:
            return {"error": "Game is not in playing state"}

        if player.station_state is None:
            return {"error": "Player station not initialized"}

        letter = letter.upper()

        # Validate letter
        if not letter.isalpha() or len(letter) != 1:
            return {"error": "Invalid letter"}

        station = player.station_state
        correct = station.guess(letter)

        result = {
            "correct": correct,
            "letter": letter,
            "revealed": station.revealed,
            "attempts_left": station.attempts_left,
            "station_complete": False,
            "station_failed": False,
            "game_won": False,
        }

        if station.is_complete:
            result["station_complete"] = True
            result["word"] = station.word

            # Check if player won
            if player.current_station >= TOTAL_STATIONS:
                result["game_won"] = True
                game.status = GameStatus.FINISHED
                game.winner = player.id
            else:
                # Advance to next station
                player.current_station += 1
                self._init_player_station(game, player)

        elif station.is_failed:
            result["station_failed"] = True
            result["word"] = station.word

            # Reset to station 1
            player.current_station = 1
            self._init_player_station(game, player)

        return result

    def get_player_station_info(self, player: HangmanPlayer) -> dict:
        """Get the current station info for a player."""
        if player.station_state is None:
            return {}

        return {
            "station": player.current_station,
            "revealed": player.station_state.revealed,
            "attempts_left": player.station_state.attempts_left,
        }

    def find_joinable_game(self) -> HangmanGame | None:
        """Find an active game in PLAYING status that has room for more players."""
        for game in self._games.values():
            if (
                game.status == GameStatus.PLAYING
                and game.player_count < MAX_PLAYERS_PER_GAME
            ):
                return game
        return None

    def add_player_to_active_game(self, game: HangmanGame, player: HangmanPlayer) -> None:
        """Add a player to an active game and initialize their station."""
        game.add_player(player)
        self._init_player_station(game, player)

    @property
    def active_games(self) -> list[HangmanGame]:
        """Get all active games."""
        return [
            game for game in self._games.values()
            if game.status != GameStatus.FINISHED
        ]


# Global singleton instance
_hangman_manager: HangmanGameManager | None = None


def get_hangman_manager() -> HangmanGameManager:
    """Get the global Hangman game manager instance."""
    global _hangman_manager
    if _hangman_manager is None:
        _hangman_manager = HangmanGameManager()
    return _hangman_manager
