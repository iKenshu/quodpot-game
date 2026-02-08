"""Duels game messages."""

from typing import Any, Literal

from pydantic import BaseModel


class SpellCastMessage(BaseModel):
    type: Literal["spell_cast"] = "spell_cast"
    spell: Literal["ignis", "aqua", "virel"]


class RematchMessage(BaseModel):
    type: Literal["rematch"] = "rematch"


class ServerMessage(BaseModel):
    type: str

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class DuelStartMessage(ServerMessage):
    type: Literal["duel_start"] = "duel_start"
    opponent_id: str
    opponent_name: str
    rounds_to_win: int


class RoundStartMessage(ServerMessage):
    type: Literal["round_start"] = "round_start"
    round_number: int


class OpponentCastMessage(ServerMessage):
    type: Literal["opponent_cast"] = "opponent_cast"
    message: str = "Tu oponente ha elegido un hechizo"


class RoundResultMessage(ServerMessage):
    type: Literal["round_result"] = "round_result"
    round_number: int
    your_spell: str
    opponent_spell: str
    result: Literal["win", "lose", "tie"]
    your_score: int
    opponent_score: int


class DuelOverMessage(ServerMessage):
    type: Literal["duel_over"] = "duel_over"
    winner_id: str
    winner_name: str
    final_score: str
    your_result: Literal["victory", "defeat"]
