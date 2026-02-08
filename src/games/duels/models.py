"""Duels game models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from models.base import BaseGame, Player


class Spell(str, Enum):
    IGNIS = "ignis"
    AQUA = "aqua"
    VIREL = "virel"


class RoundResult(str, Enum):
    PLAYER1_WINS = "player1_wins"
    PLAYER2_WINS = "player2_wins"
    TIE = "tie"


@dataclass
class SpellCast:
    player_id: str
    spell: Spell
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Round:
    round_number: int
    player1_cast: SpellCast | None = None
    player2_cast: SpellCast | None = None
    result: RoundResult | None = None

    def is_complete(self) -> bool:
        return self.player1_cast is not None and self.player2_cast is not None

    def determine_winner(self) -> RoundResult:
        if not self.is_complete():
            raise ValueError("Cannot determine winner: round is not complete")

        spell1 = self.player1_cast.spell
        spell2 = self.player2_cast.spell

        if spell1 == spell2:
            return RoundResult.TIE

        wins = {
            (Spell.IGNIS, Spell.VIREL): RoundResult.PLAYER1_WINS,
            (Spell.VIREL, Spell.AQUA): RoundResult.PLAYER1_WINS,
            (Spell.AQUA, Spell.IGNIS): RoundResult.PLAYER1_WINS,
            (Spell.VIREL, Spell.IGNIS): RoundResult.PLAYER2_WINS,
            (Spell.AQUA, Spell.VIREL): RoundResult.PLAYER2_WINS,
            (Spell.IGNIS, Spell.AQUA): RoundResult.PLAYER2_WINS,
        }

        return wins[(spell1, spell2)]


@dataclass
class DuelGame(BaseGame):
    rounds: list[Round] = field(default_factory=list)
    player1_id: str = ""
    player2_id: str = ""
    player1_score: int = 0
    player2_score: int = 0
    rounds_to_win: int = 2
    game_mode: str = "pvp"  # "pvp" or "pve"
    player_wrappers: dict = field(default_factory=dict)  # MessageReceiver wrappers

    def __post_init__(self):
        if not self.rounds:
            self.rounds.append(Round(round_number=1))

    @property
    def current_round(self) -> Round:
        return self.rounds[-1]

    def process_spell_cast(self, player_id: str, spell: Spell) -> bool:
        if player_id not in (self.player1_id, self.player2_id):
            raise ValueError(f"Player {player_id} is not in this duel")

        current = self.current_round
        cast = SpellCast(player_id=player_id, spell=spell)

        if player_id == self.player1_id:
            if current.player1_cast is not None:
                raise ValueError("Player 1 has already cast a spell this round")
            current.player1_cast = cast
        else:
            if current.player2_cast is not None:
                raise ValueError("Player 2 has already cast a spell this round")
            current.player2_cast = cast

        return current.is_complete()

    def resolve_current_round(self) -> RoundResult:
        current = self.current_round
        result = current.determine_winner()
        current.result = result

        if result == RoundResult.PLAYER1_WINS:
            self.player1_score += 1
        elif result == RoundResult.PLAYER2_WINS:
            self.player2_score += 1

        return result

    def check_game_over(self) -> bool:
        return (
            self.player1_score >= self.rounds_to_win
            or self.player2_score >= self.rounds_to_win
        )

    def start_new_round(self) -> None:
        if not self.current_round.is_complete():
            raise ValueError("Cannot start new round: current round is not complete")

        next_round_number = len(self.rounds) + 1
        self.rounds.append(Round(round_number=next_round_number))
