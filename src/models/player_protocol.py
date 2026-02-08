"""Player protocols for different player types."""

from typing import Protocol, runtime_checkable
from models.messages import ServerMessage


@runtime_checkable
class MessageReceiver(Protocol):
    """Protocol for entities that can receive game messages."""

    async def send_message(self, message: ServerMessage) -> None:
        """Send a message to this receiver."""
        ...


@runtime_checkable
class PlayerIdentity(Protocol):
    """Protocol for core player identity."""

    @property
    def id(self) -> str:
        """Unique player identifier."""
        ...

    @property
    def name(self) -> str:
        """Player display name."""
        ...

    @property
    def connected(self) -> bool:
        """Whether player is connected."""
        ...
