"""Strategy pattern for spell selection in duels."""

from abc import ABC, abstractmethod
import asyncio
import random
from .models import DuelGame, Spell


class SpellSelectionStrategy(ABC):
    """Abstract strategy for selecting spells."""

    @abstractmethod
    async def select_spell(self, game: DuelGame, player_id: str) -> Spell:
        """Select a spell for the given player in the game."""
        pass


class RandomAISpellSelection(SpellSelectionStrategy):
    """AI that selects random spells."""

    def __init__(self, delay_seconds: float = 1.5):
        self.delay_seconds = delay_seconds

    async def select_spell(self, game: DuelGame, player_id: str) -> Spell:
        """Choose a random spell after a delay to simulate thinking."""
        await asyncio.sleep(self.delay_seconds)
        return random.choice([Spell.IGNIS, Spell.AQUA, Spell.VIREL])


class HumanSpellSelection(SpellSelectionStrategy):
    """Human spell selection (waits for WebSocket input)."""

    async def select_spell(self, game: DuelGame, player_id: str) -> Spell:
        """This is a placeholder - actual selection happens via WebSocket events."""
        raise NotImplementedError("Human selection happens via WebSocket messages")
