"""PVE service for managing AI opponents in duels."""

from config import AI_PLAYER_NAME, AI_RESPONSE_DELAY_SECONDS
from models.player_wrapper import AIPlayerWrapper
from .spell_strategy import RandomAISpellSelection, SpellSelectionStrategy


class PVEService:
    """Service for managing AI opponents in PVE duels."""

    def __init__(self, spell_strategy: SpellSelectionStrategy | None = None):
        self.spell_strategy = spell_strategy or RandomAISpellSelection(
            delay_seconds=AI_RESPONSE_DELAY_SECONDS
        )

    def create_ai_player(self, game_id: str) -> AIPlayerWrapper:
        """Create an AI player for PVE game."""
        ai_id = f"ai_{game_id}"
        return AIPlayerWrapper(
            player_id=ai_id,
            player_name=AI_PLAYER_NAME,
        )

    async def get_ai_spell_choice(self, game, ai_player_id):
        """Get AI's spell choice using the strategy."""
        spell = await self.spell_strategy.select_spell(game, ai_player_id)
        return spell
