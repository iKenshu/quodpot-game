"""Player wrapper for backward compatibility with protocols."""

from dataclasses import dataclass
from fastapi import WebSocket
from models.base import Player
from models.messages import ServerMessage


@dataclass
class HumanPlayerWrapper:
    """Wraps Player with WebSocket for human players."""

    player: Player
    websocket: WebSocket

    @property
    def id(self) -> str:
        return self.player.id

    @property
    def name(self) -> str:
        return self.player.name

    @property
    def connected(self) -> bool:
        return self.player.connected

    async def send_message(self, message: ServerMessage) -> None:
        """Send message via WebSocket."""
        if not self.websocket or not self.connected:
            return
        
        if self.websocket.client_state.name != "CONNECTED":
            return

        try:
            import json
            await self.websocket.send_text(json.dumps(message.to_dict()))
        except Exception:
            pass


@dataclass
class AIPlayerWrapper:
    """Wraps player identity for AI opponents."""

    player_id: str
    player_name: str

    @property
    def id(self) -> str:
        return self.player_id

    @property
    def name(self) -> str:
        return self.player_name

    @property
    def connected(self) -> bool:
        return True

    async def send_message(self, message: ServerMessage) -> None:
        """AI players don't receive messages."""
        pass
