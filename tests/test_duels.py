"""Tests for duels game logic."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from config import DUELS_ROUNDS_TO_WIN
from games.duels.manager import DuelsManager
from games.duels.models import DuelGame, Round, RoundResult, Spell, SpellCast
from models.base import GameStatus, Player


class TestSpell:
    """Tests for Spell enum."""

    def test_spell_values(self):
        assert Spell.IGNIS.value == "ignis"
        assert Spell.AQUA.value == "aqua"
        assert Spell.VIREL.value == "virel"

    def test_spell_from_string(self):
        assert Spell("ignis") == Spell.IGNIS
        assert Spell("aqua") == Spell.AQUA
        assert Spell("virel") == Spell.VIREL


class TestRound:
    """Tests for Round class."""

    def test_round_not_complete_initially(self):
        round = Round(round_number=1)
        assert not round.is_complete()

    def test_round_not_complete_with_one_cast(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        assert not round.is_complete()

    def test_round_complete_with_both_casts(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.AQUA)
        assert round.is_complete()

    def test_determine_winner_ignis_beats_virel(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.VIREL)
        assert round.determine_winner() == RoundResult.PLAYER1_WINS

    def test_determine_winner_virel_beats_aqua(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.VIREL)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.AQUA)
        assert round.determine_winner() == RoundResult.PLAYER1_WINS

    def test_determine_winner_aqua_beats_ignis(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.AQUA)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.IGNIS)
        assert round.determine_winner() == RoundResult.PLAYER1_WINS

    def test_determine_winner_virel_beats_ignis(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.VIREL)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.IGNIS)
        assert round.determine_winner() == RoundResult.PLAYER2_WINS

    def test_determine_winner_aqua_beats_virel(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.AQUA)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.VIREL)
        assert round.determine_winner() == RoundResult.PLAYER2_WINS

    def test_determine_winner_ignis_beats_aqua(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.AQUA)
        assert round.determine_winner() == RoundResult.PLAYER2_WINS

    def test_determine_winner_tie_ignis(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.IGNIS)
        assert round.determine_winner() == RoundResult.TIE

    def test_determine_winner_tie_aqua(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.AQUA)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.AQUA)
        assert round.determine_winner() == RoundResult.TIE

    def test_determine_winner_tie_virel(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.VIREL)
        round.player2_cast = SpellCast(player_id="p2", spell=Spell.VIREL)
        assert round.determine_winner() == RoundResult.TIE

    def test_determine_winner_raises_when_not_complete(self):
        round = Round(round_number=1)
        round.player1_cast = SpellCast(player_id="p1", spell=Spell.IGNIS)
        with pytest.raises(ValueError, match="round is not complete"):
            round.determine_winner()


class TestDuelGame:
    """Tests for DuelGame class."""

    def test_create_game(self):
        game = DuelGame(
            id="TEST123",
            game_type="duels",
            rounds_to_win=2,
            round_timer_seconds=15,
        )
        assert game.id == "TEST123"
        assert game.game_type == "duels"
        assert game.status == GameStatus.WAITING
        assert len(game.rounds) == 1
        assert game.current_round.round_number == 1

    def test_process_spell_cast_player1(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        complete = game.process_spell_cast("p1", Spell.IGNIS)
        assert not complete
        assert game.current_round.player1_cast is not None
        assert game.current_round.player1_cast.spell == Spell.IGNIS

    def test_process_spell_cast_player2(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        complete = game.process_spell_cast("p2", Spell.AQUA)
        assert not complete
        assert game.current_round.player2_cast is not None
        assert game.current_round.player2_cast.spell == Spell.AQUA

    def test_process_spell_cast_completes_round(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        complete = game.process_spell_cast("p2", Spell.AQUA)
        assert complete

    def test_process_spell_cast_rejects_double_cast(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        with pytest.raises(ValueError, match="has already cast a spell"):
            game.process_spell_cast("p1", Spell.AQUA)

    def test_process_spell_cast_rejects_invalid_player(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        with pytest.raises(ValueError, match="not in this duel"):
            game.process_spell_cast("p3", Spell.IGNIS)

    def test_resolve_current_round_player1_wins(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        game.process_spell_cast("p2", Spell.VIREL)
        result = game.resolve_current_round()
        assert result == RoundResult.PLAYER1_WINS
        assert game.player1_score == 1
        assert game.player2_score == 0

    def test_resolve_current_round_player2_wins(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        game.process_spell_cast("p2", Spell.AQUA)
        result = game.resolve_current_round()
        assert result == RoundResult.PLAYER2_WINS
        assert game.player1_score == 0
        assert game.player2_score == 1

    def test_resolve_current_round_tie(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        game.process_spell_cast("p2", Spell.IGNIS)
        result = game.resolve_current_round()
        assert result == RoundResult.TIE
        assert game.player1_score == 0
        assert game.player2_score == 0

    def test_check_game_over_not_over(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_score=1,
            player2_score=0,
            rounds_to_win=2,
        )
        assert not game.check_game_over()

    def test_check_game_over_player1_wins(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_score=2,
            player2_score=0,
            rounds_to_win=2,
        )
        assert game.check_game_over()

    def test_check_game_over_player2_wins(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_score=0,
            player2_score=2,
            rounds_to_win=2,
        )
        assert game.check_game_over()

    def test_start_new_round(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        game.process_spell_cast("p1", Spell.IGNIS)
        game.process_spell_cast("p2", Spell.AQUA)
        game.resolve_current_round()
        game.start_new_round()
        assert len(game.rounds) == 2
        assert game.current_round.round_number == 2
        assert not game.current_round.is_complete()

    def test_start_new_round_raises_when_not_complete(self):
        game = DuelGame(
            id="TEST",
            game_type="duels",
            player1_id="p1",
            player2_id="p2",
        )
        with pytest.raises(ValueError, match="current round is not complete"):
            game.start_new_round()


class TestDuelsManager:
    """Tests for DuelsManager class."""

    def test_create_game(self):
        manager = DuelsManager()
        game = manager.create_game()
        assert game is not None
        assert game.game_type == "duels"
        assert game.rounds_to_win == DUELS_ROUNDS_TO_WIN
        assert game.round_timer_seconds == DUELS_ROUND_TIMER
        assert game.id in manager._games

    def test_get_game(self):
        manager = DuelsManager()
        game = manager.create_game()
        retrieved = manager.get_game(game.id)
        assert retrieved == game

    def test_get_game_returns_none_for_invalid_id(self):
        manager = DuelsManager()
        assert manager.get_game("INVALID") is None

    def test_remove_game(self):
        manager = DuelsManager()
        game = manager.create_game()
        manager.remove_game(game.id)
        assert manager.get_game(game.id) is None

    def test_start_game(self):
        manager = DuelsManager()
        game = manager.create_game()
        ws1, ws2 = MagicMock(), MagicMock()
        player1 = Player.create("Player1", ws1)
        player2 = Player.create("Player2", ws2)
        game.add_player(player1)
        game.add_player(player2)

        manager.start_game(game)
        assert game.status == GameStatus.PLAYING
        assert game.player1_id == player1.id
        assert game.player2_id == player2.id

    def test_start_game_raises_with_wrong_player_count(self):
        manager = DuelsManager()
        game = manager.create_game()
        ws = MagicMock()
        player = Player.create("Player1", ws)
        game.add_player(player)

        with pytest.raises(ValueError, match="requires exactly 2 players"):
            manager.start_game(game)

    def test_process_spell_cast_returns_false_when_not_complete(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.player1_id = "p1"
        game.player2_id = "p2"

        round_complete, result = manager.process_spell_cast(game, "p1", Spell.IGNIS)
        assert not round_complete
        assert result is None

    def test_process_spell_cast_returns_result_when_complete(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.player1_id = "p1"
        game.player2_id = "p2"

        manager.process_spell_cast(game, "p1", Spell.IGNIS)
        round_complete, result = manager.process_spell_cast(game, "p2", Spell.VIREL)
        assert round_complete
        assert result == RoundResult.PLAYER1_WINS

    def test_auto_cast_for_pending_players_casts_for_player1(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.player1_id = "p1"
        game.player2_id = "p2"
        game.process_spell_cast("p2", Spell.AQUA)

        manager.auto_cast_for_pending_players(game)
        assert game.current_round.player1_cast is not None
        assert game.current_round.is_complete()

    def test_auto_cast_for_pending_players_casts_for_player2(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.player1_id = "p1"
        game.player2_id = "p2"
        game.process_spell_cast("p1", Spell.IGNIS)

        manager.auto_cast_for_pending_players(game)
        assert game.current_round.player2_cast is not None
        assert game.current_round.is_complete()

    def test_auto_cast_for_pending_players_casts_for_both(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.player1_id = "p1"
        game.player2_id = "p2"

        manager.auto_cast_for_pending_players(game)
        assert game.current_round.player1_cast is not None
        assert game.current_round.player2_cast is not None
        assert game.current_round.is_complete()

    def test_cancel_round_timer(self):
        manager = DuelsManager()
        game = manager.create_game()
        task = MagicMock()
        manager._round_timers[game.id] = task

        manager.cancel_round_timer(game.id)
        task.cancel.assert_called_once()
        assert game.id not in manager._round_timers

    @pytest.mark.asyncio
    async def test_start_round_timer_calls_callback_after_timeout(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.round_timer_seconds = 0.1
        callback_called = False

        async def mock_callback(game_id):
            nonlocal callback_called
            callback_called = True

        await manager.start_round_timer(game.id, mock_callback)
        await asyncio.sleep(0.2)
        assert callback_called

    @pytest.mark.asyncio
    async def test_start_round_timer_cancels_previous_timer(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.round_timer_seconds = 1
        callback1_called = False
        callback2_called = False

        async def callback1(game_id):
            nonlocal callback1_called
            callback1_called = True

        async def callback2(game_id):
            nonlocal callback2_called
            callback2_called = True

        await manager.start_round_timer(game.id, callback1)
        await asyncio.sleep(0.05)
        await manager.start_round_timer(game.id, callback2)
        await asyncio.sleep(0.05)
        assert not callback1_called

    def test_active_games(self):
        manager = DuelsManager()
        game1 = manager.create_game()
        game2 = manager.create_game()
        game2.status = GameStatus.FINISHED

        active = manager.active_games
        assert len(active) == 1
        assert game1 in active
        assert game2 not in active


class TestDuelsIntegration:
    """Integration tests for complete duel flows."""

    def test_complete_duel_best_of_three(self):
        manager = DuelsManager()
        game = manager.create_game()
        ws1, ws2 = MagicMock(), MagicMock()
        player1 = Player.create("Player1", ws1)
        player2 = Player.create("Player2", ws2)
        game.add_player(player1)
        game.add_player(player2)
        manager.start_game(game)

        game.process_spell_cast(player1.id, Spell.IGNIS)
        game.process_spell_cast(player2.id, Spell.VIREL)
        result = game.resolve_current_round()
        assert result == RoundResult.PLAYER1_WINS
        assert game.player1_score == 1
        assert not game.check_game_over()

        game.start_new_round()
        game.process_spell_cast(player1.id, Spell.IGNIS)
        game.process_spell_cast(player2.id, Spell.VIREL)
        result = game.resolve_current_round()
        assert result == RoundResult.PLAYER1_WINS
        assert game.player1_score == 2
        assert game.check_game_over()

    def test_complete_duel_with_tie(self):
        manager = DuelsManager()
        game = manager.create_game()
        ws1, ws2 = MagicMock(), MagicMock()
        player1 = Player.create("Player1", ws1)
        player2 = Player.create("Player2", ws2)
        game.add_player(player1)
        game.add_player(player2)
        manager.start_game(game)

        game.process_spell_cast(player1.id, Spell.IGNIS)
        game.process_spell_cast(player2.id, Spell.IGNIS)
        result = game.resolve_current_round()
        assert result == RoundResult.TIE
        assert game.player1_score == 0
        assert game.player2_score == 0
        assert not game.check_game_over()

        game.start_new_round()
        game.process_spell_cast(player1.id, Spell.AQUA)
        game.process_spell_cast(player2.id, Spell.VIREL)
        result = game.resolve_current_round()
        assert result == RoundResult.PLAYER2_WINS
        assert game.player2_score == 1

    @pytest.mark.asyncio
    async def test_timeout_auto_casts_and_resolves(self):
        manager = DuelsManager()
        game = manager.create_game()
        game.round_timer_seconds = 0.1
        ws1, ws2 = MagicMock(), MagicMock()
        player1 = Player.create("Player1", ws1)
        player2 = Player.create("Player2", ws2)
        game.add_player(player1)
        game.add_player(player2)
        manager.start_game(game)

        timeout_called = False

        async def timeout_callback(game_id):
            nonlocal timeout_called
            timeout_called = True
            game = manager.get_game(game_id)
            manager.auto_cast_for_pending_players(game)
            game.resolve_current_round()

        await manager.start_round_timer(game.id, timeout_callback)
        await asyncio.sleep(0.2)

        assert timeout_called
        assert game.current_round.is_complete()
        assert game.player1_score + game.player2_score >= 0
