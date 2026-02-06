"""WebSocket connection handler."""

import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from ..config import GAME_TYPE_HANGMAN
from ..models.base import BaseGame
from ..models.messages import ErrorMessage, ServerMessage
from ..services.matchmaking import get_matchmaking
from .router import GameRouter

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and message routing.

    This class is responsible ONLY for managing WebSocket connections
    and delegating message routing to GameRouter. It does NOT contain
    game-specific logic.
    """

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._game_router = GameRouter(self)
        self._matchmaking = get_matchmaking()

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to handle
        """
        await websocket.accept()
        player_id: str | None = None

        logger.info("New WebSocket connection accepted")

        try:
            async for message in websocket.iter_text():
                player_id = await self._process_message(websocket, message, player_id)

        except WebSocketDisconnect:
            logger.info(
                "WebSocket disconnected",
                extra={"player_id": player_id} if player_id else {},
            )
            if player_id:
                await self._handle_disconnect(player_id)

    async def _process_message(
        self, websocket: WebSocket, message: str, player_id: str | None
    ) -> str | None:
        """Process a single message from the WebSocket.

        Args:
            websocket: The WebSocket connection
            message: Raw message text
            player_id: Current player ID if authenticated

        Returns:
            Updated player_id (may be set on first join)
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            logger.warning(f"Received invalid JSON: {e}", extra={"message": message})
            await self.send_error(websocket, "Invalid JSON")
            return player_id

        result = await self._game_router.process(websocket, data, player_id)

        if result and "player_id" in result:
            new_player_id = result["player_id"]
            if (
                new_player_id in self._connections
                and self._connections[new_player_id] != websocket
            ):
                logger.warning(
                    f"Player {new_player_id} reconnecting, replacing old connection",
                    extra={"player_id": new_player_id},
                )
            self._connections[new_player_id] = websocket
            logger.info("Player connected", extra={"player_id": new_player_id})
            return new_player_id

        return player_id

    async def _handle_disconnect(self, player_id: str) -> None:
        """Handle a player disconnection.

        Delegates to GameRouter for game-specific cleanup.
        Only handles connection cleanup here.

        Args:
            player_id: The ID of the player disconnecting
        """
        self._connections.pop(player_id, None)
        fake_leave = {"type": "leave"}
        websocket = self._connections.get(player_id)

        try:
            await self._game_router.process(
                websocket if websocket else None,  # May be None
                fake_leave,
                player_id,
            )
        except Exception as e:
            logger.error(
                f"Error during disconnect cleanup, doing manual cleanup: {e}",
                extra={"player_id": player_id},
                exc_info=True,
            )
            self._matchmaking.remove_player(player_id)
            self._matchmaking.remove_player_from_game(player_id)

    async def send_to_player(self, player_id: str, message: ServerMessage) -> None:
        """Send a message to a specific player by their ID.

        Args:
            player_id: The ID of the player to send to
            message: The message to send
        """
        websocket = self._connections.get(player_id)
        if websocket:
            await self.send_to_websocket(websocket, message)
        else:
            logger.debug(
                f"Cannot send to player {player_id}: not connected",
                extra={"player_id": player_id, "message_type": type(message).__name__},
            )

    async def send_to_websocket(
        self, websocket: WebSocket, message: ServerMessage
    ) -> None:
        """Send a message directly to a WebSocket connection.

        Args:
            websocket: The WebSocket to send to
            message: The message to send
        """
        if websocket is None:
            return

        try:
            await websocket.send_text(json.dumps(message.to_dict()))
        except Exception as e:
            logger.warning(
                f"Failed to send message: {e}",
                extra={"message_type": type(message).__name__},
            )

    async def broadcast_to_game(self, game: BaseGame, message: ServerMessage) -> None:
        """Broadcast a message to all players in a game."""
        for player in game.connected_players:
            await self.send_to_player(player.id, message)

    async def broadcast_to_game_except(
        self, game: BaseGame, message: ServerMessage, except_player_id: str
    ) -> None:
        """Broadcast a message to all players except one."""
        for player in game.connected_players:
            if player.id != except_player_id:
                await self.send_to_player(player.id, message)

    async def broadcast_to_queue(
        self, message: ServerMessage, game_type: str = GAME_TYPE_HANGMAN
    ) -> None:
        """Broadcast a message to all players in a specific game type queue.

        Args:
            message: The message to broadcast
            game_type: The game type queue to broadcast to (default: hangman)
        """
        for player in self._matchmaking.get_queued_players(game_type):
            await self.send_to_player(player.id, message)

    async def send_error(self, websocket: WebSocket, error_message: str) -> None:
        """Send an error message to a websocket."""
        await self.send_to_websocket(websocket, ErrorMessage(message=error_message))


_ws_handler: WebSocketHandler | None = None


def get_ws_handler() -> WebSocketHandler:
    """Get the global WebSocket handler instance."""
    global _ws_handler
    if _ws_handler is None:
        _ws_handler = WebSocketHandler()
    return _ws_handler
