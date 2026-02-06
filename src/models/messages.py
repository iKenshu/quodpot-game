"""Base WebSocket message models shared across games."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class JoinMessage(BaseModel):
    type: Literal["join"] = "join"
    player_name: str = Field(..., min_length=1, max_length=20)
    game_type: str = Field(default="hangman")  # Default for backward compatibility


class LeaveMessage(BaseModel):
    type: Literal["leave"] = "leave"


class ClientMessage(BaseModel):
    """Union type for common client messages."""

    type: str

    @classmethod
    def parse(cls, data: dict) -> JoinMessage | LeaveMessage | None:
        """Parse a raw message into the appropriate type."""
        msg_type = data.get("type")
        try:
            if msg_type == "join":
                return JoinMessage(**data)
            elif msg_type == "leave":
                return LeaveMessage(**data)
        except Exception:
            return None
        return None


class ServerMessage(BaseModel):
    """Base class for server messages."""

    type: str

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class JoinedMessage(ServerMessage):
    type: Literal["joined"] = "joined"
    player_id: str
    game_id: str
    player_name: str


class WaitingMessage(ServerMessage):
    type: Literal["waiting"] = "waiting"
    players_in_queue: int
    message: str


class ErrorMessage(ServerMessage):
    type: Literal["error"] = "error"
    message: str
    type: Literal["error"] = "error"
    message: str
