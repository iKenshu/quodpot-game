"""tests for PVE mode."""

from unittest.mock import MagicMock

import pytest

from games.duels.manager import DuelsManager
from games.duels.models import RoundResult, Spell
from games.duels.pve_service import PVEService
from games.duels.spell_strategy import RandomAISpellSelection
from models.base import Player
from models.player_wrapper import AIPlayerWrapper, HumanPlayerWrapper


class TestPVE:
    """Test PVE mode end-to-end."""

    def test_create_pve_game(self):
        """Test creating a PVE game with AI opponent."""
        manager = DuelsManager()
        pve_service = PVEService()
        human_player = Player.create("Human Player", MagicMock())
        game = manager.create_pve_game(human_player, pve_service)

        assert game.game_mode == "pve"

        assert len(game.players) == 2

        ai_player_id = [pid for pid in game.players.keys() if pid.startswith("ai_")][0]
        ai_player = game.get_player(ai_player_id)
        assert ai_player is not None
        assert ai_player.name == "Guardián Arcano"

        assert len(game.player_wrappers) == 2
        assert human_player.id in game.player_wrappers
        assert ai_player_id in game.player_wrappers

        ai_wrapper = game.player_wrappers[ai_player_id]
        assert isinstance(ai_wrapper, AIPlayerWrapper)

        human_wrapper = game.player_wrappers[human_player.id]
        assert isinstance(human_wrapper, HumanPlayerWrapper)

    def test_ai_player_wrapper_properties(self):
        """Test AI player wrapper properties."""
        pve_service = PVEService()
        ai_wrapper = pve_service.create_ai_player("game_123")

        assert ai_wrapper.id == "ai_game_123"
        assert ai_wrapper.name == "Guardián Arcano"
        assert ai_wrapper.connected is True

    @pytest.mark.asyncio
    async def test_ai_spell_selection(self):
        """Test AI spell selection strategy."""
        pve_service = PVEService(spell_strategy=RandomAISpellSelection(delay_seconds=0))

        manager = DuelsManager()
        human_player = Player.create("Human", MagicMock())
        game = manager.create_pve_game(human_player, pve_service)

        ai_player_id = [pid for pid in game.players.keys() if pid.startswith("ai_")][0]

        spell = await pve_service.get_ai_spell_choice(game, ai_player_id)

        assert isinstance(spell, Spell)
        assert spell in [Spell.IGNIS, Spell.AQUA, Spell.VIREL]

    @pytest.mark.asyncio
    async def test_complete_pve_round(self):
        """Test a complete PVE round."""
        pve_service = PVEService(spell_strategy=RandomAISpellSelection(delay_seconds=0))

        manager = DuelsManager()
        human_player = Player.create("Human", MagicMock())
        game = manager.create_pve_game(human_player, pve_service)

        manager.start_game(game)

        ai_player_id = [pid for pid in game.players.keys() if pid.startswith("ai_")][0]

        round_complete, result = manager.process_spell_cast(
            game, human_player.id, Spell.IGNIS
        )
        assert not round_complete
        assert result is None

        ai_spell = await pve_service.get_ai_spell_choice(game, ai_player_id)
        round_complete, result = manager.process_spell_cast(
            game, ai_player_id, ai_spell
        )

        assert round_complete
        assert isinstance(result, RoundResult)

        assert game.player1_score + game.player2_score >= 0

    def test_ai_wrapper_send_message_is_noop(self):
        """Test that AI wrapper send_message is a no-op."""
        pve_service = PVEService()
        ai_wrapper = pve_service.create_ai_player("test")

        import asyncio

        from models.messages import ServerMessage

        async def test():
            await ai_wrapper.send_message(ServerMessage(type="test"))

        asyncio.run(test())

    def test_game_mode_pvp_by_default(self):
        """Test that regular games default to PVP mode."""
        manager = DuelsManager()
        game = manager.create_game()

        assert game.game_mode == "pvp"

    @pytest.mark.asyncio
    async def test_spell_strategy_randomness(self):
        """Test that AI spell selection is random."""
        strategy = RandomAISpellSelection(delay_seconds=0)
        manager = DuelsManager()

        human_player = Player.create("Human", MagicMock())
        game = manager.create_pve_game(
            human_player, PVEService(spell_strategy=strategy)
        )

        spells = []
        for _ in range(20):
            spell = await strategy.select_spell(game, "ai_test")
            spells.append(spell)

        unique_spells = set(spells)
        assert len(unique_spells) >= 2

        for spell in spells:
            assert spell in [Spell.IGNIS, Spell.AQUA, Spell.VIREL]
        for spell in spells:
            assert spell in [Spell.IGNIS, Spell.AQUA, Spell.VIREL]
