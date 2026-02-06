"""WebSocket message models."""

from typing import Literal, Any
from pydantic import BaseModel, Field


# Client -> Server Messages

class JoinMessage(BaseModel):
    type: Literal["join"] = "join"
    player_name: str = Field(..., min_length=1, max_length=20)


class GuessMessage(BaseModel):
    type: Literal["guess"] = "guess"
    letter: str = Field(..., min_length=1, max_length=1)


class LeaveMessage(BaseModel):
    type: Literal["leave"] = "leave"


class ClientMessage(BaseModel):
    """Union type for all client messages."""
    type: str

    @classmethod
    def parse(cls, data: dict) -> JoinMessage | GuessMessage | LeaveMessage | None:
        """Parse a raw message into the appropriate type."""
        msg_type = data.get("type")
        try:
            if msg_type == "join":
                return JoinMessage(**data)
            elif msg_type == "guess":
                return GuessMessage(**data)
            elif msg_type == "leave":
                return LeaveMessage(**data)
        except Exception:
            return None
        return None


# Server -> Client Messages

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


class GameStartMessage(ServerMessage):
    type: Literal["game_start"] = "game_start"
    players: list[dict[str, str]]  # [{"id": "...", "name": "..."}, ...]
    total_stations: int


class StationUpdateMessage(ServerMessage):
    type: Literal["station_update"] = "station_update"
    station: int
    revealed: str
    attempts_left: int


class CorrectGuessMessage(ServerMessage):
    type: Literal["correct_guess"] = "correct_guess"
    letter: str
    revealed: str


class WrongGuessMessage(ServerMessage):
    type: Literal["wrong_guess"] = "wrong_guess"
    letter: str
    attempts_left: int


class StationCompleteMessage(ServerMessage):
    type: Literal["station_complete"] = "station_complete"
    station: int
    word: str


class StationFailedMessage(ServerMessage):
    type: Literal["station_failed"] = "station_failed"
    reset_to: int
    word: str


class PlayerProgressMessage(ServerMessage):
    type: Literal["player_progress"] = "player_progress"
    player_id: str
    player_name: str
    station: int


class PlayerJoinedMessage(ServerMessage):
    type: Literal["player_joined"] = "player_joined"
    player_id: str
    player_name: str
    station: int


class GameOverMessage(ServerMessage):
    type: Literal["game_over"] = "game_over"
    winner_id: str
    winner_name: str
    words: list[str]


class ErrorMessage(ServerMessage):
    type: Literal["error"] = "error"
    message: str


class StationStatusMessage(ServerMessage):
    """Broadcast message with player distribution across stations."""
    type: Literal["station_status"] = "station_status"
    stations: dict[int, list[str]]  # {station_number: [player_names]}
