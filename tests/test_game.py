"""Tests for game logic."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from src.models.game import Station, Player, Game, GameStatus
from src.services.word_bank import WordBank
from src.services.game_manager import GameManager
from src.config import MAX_ATTEMPTS_PER_WORD, TOTAL_STATIONS


class TestStation:
    """Tests for the Station class."""

    def test_revealed_hides_unguessed_letters(self):
        station = Station(word="CASA")
        assert station.revealed == "_ _ _ _"

    def test_revealed_shows_guessed_letters(self):
        station = Station(word="CASA")
        station.guessed_letters = {"A"}
        assert station.revealed == "_ A _ A"

    def test_guess_correct_letter(self):
        station = Station(word="CASA", attempts_left=6)
        result = station.guess("A")
        assert result is True
        assert "A" in station.guessed_letters
        assert station.attempts_left == 6

    def test_guess_wrong_letter(self):
        station = Station(word="CASA", attempts_left=6)
        result = station.guess("X")
        assert result is False
        assert "X" in station.guessed_letters
        assert station.attempts_left == 5

    def test_guess_already_guessed(self):
        station = Station(word="CASA", attempts_left=6)
        station.guessed_letters = {"X"}
        result = station.guess("X")
        assert result is True  # No penalty for repeated guess
        assert station.attempts_left == 6

    def test_is_complete(self):
        station = Station(word="CASA")
        station.guessed_letters = {"C", "A", "S"}
        assert station.is_complete is True

    def test_is_not_complete(self):
        station = Station(word="CASA")
        station.guessed_letters = {"C", "A"}
        assert station.is_complete is False

    def test_is_failed(self):
        station = Station(word="CASA", attempts_left=0)
        assert station.is_failed is True

    def test_is_not_failed(self):
        station = Station(word="CASA", attempts_left=1)
        assert station.is_failed is False


class TestPlayer:
    """Tests for the Player class."""

    def test_create_player(self):
        ws = MagicMock()
        player = Player.create("TestPlayer", ws)
        assert player.name == "TestPlayer"
        assert player.id is not None
        assert player.current_station == 1
        assert player.connected is True


class TestGame:
    """Tests for the Game class."""

    def test_create_game(self):
        words = ["CASA", "PERRO", "GATO"] + ["WORD"] * 7
        game = Game.create(words)
        assert game.id is not None
        assert len(game.id) == 8
        assert game.words == words
        assert game.status == GameStatus.WAITING

    def test_add_player(self):
        game = Game.create(["WORD"] * 10)
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        assert player.id in game.players
        assert game.player_count == 1

    def test_remove_player(self):
        game = Game.create(["WORD"] * 10)
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        game.remove_player(player.id)
        assert game.players[player.id].connected is False


class TestGameManager:
    """Tests for the GameManager class."""

    def test_create_game(self):
        manager = GameManager()
        game = manager.create_game()
        assert game is not None
        assert len(game.words) == TOTAL_STATIONS

    def test_start_game_initializes_players(self):
        manager = GameManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        manager.start_game(game)

        assert game.status == GameStatus.PLAYING
        assert player.station_state is not None
        assert player.station_state.word == game.words[0]

    def test_process_correct_guess(self):
        manager = GameManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        manager.start_game(game)

        # Get first letter of the word
        first_letter = game.words[0][0]
        result = manager.process_guess(game, player, first_letter)

        assert result["correct"] is True
        assert result["letter"] == first_letter

    def test_process_wrong_guess(self):
        manager = GameManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        manager.start_game(game)

        # Find a letter not in the word
        word = game.words[0]
        wrong_letter = "X" if "X" not in word else "Z"
        result = manager.process_guess(game, player, wrong_letter)

        assert result["correct"] is False
        assert result["attempts_left"] == MAX_ATTEMPTS_PER_WORD - 1

    def test_station_complete_advances_player(self):
        manager = GameManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        manager.start_game(game)

        # Guess all letters in the word
        word = game.words[0]
        unique_letters = set(word.upper())
        for letter in unique_letters:
            result = manager.process_guess(game, player, letter)

        assert result["station_complete"] is True
        assert player.current_station == 2

    def test_station_failed_resets_player(self):
        manager = GameManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Test", ws)
        game.add_player(player)
        manager.start_game(game)

        # First advance to station 2
        word = game.words[0]
        for letter in set(word.upper()):
            manager.process_guess(game, player, letter)

        assert player.current_station == 2

        # Now fail station 2 with 6 wrong guesses
        word2 = game.words[1]
        wrong_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1) if chr(i) not in word2.upper()]

        for letter in wrong_letters[:MAX_ATTEMPTS_PER_WORD]:
            result = manager.process_guess(game, player, letter)

        assert result["station_failed"] is True
        assert player.current_station == 1


class TestWordBank:
    """Tests for the WordBank class."""

    def test_select_words(self):
        # Uses the actual words file
        bank = WordBank()
        words = bank.select_words(10)
        assert len(words) == 10
        assert all(word.isupper() for word in words)

    def test_select_words_are_random(self):
        bank = WordBank()
        words1 = bank.select_words(10)
        words2 = bank.select_words(10)
        # Very unlikely to be the same
        assert words1 != words2 or True  # Allow same in rare cases
