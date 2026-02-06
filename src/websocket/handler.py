"""WebSocket connection handler."""

import json
from fastapi import WebSocket, WebSocketDisconnect

from ..models.base import Player, BaseGame
from ..models.messages import ServerMessage, ErrorMessage
from ..services.matchmaking import get_matchmaking
from ..games.hangman.manager import get_hangman_manager
from .router import GameRouter


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}  # player_id -> websocket
        self._game_router = GameRouter(self)

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle a new WebSocket connection."""
        await websocket.accept()
        player_id: str | None = None

        try:
            async for message in websocket.iter_text():
                try:
                    data = json.loads(message)
                    result = await self._game_router.process(websocket, data, player_id)

                    if result and "player_id" in result:
                        player_id = result["player_id"]
                        self._connections[player_id] = websocket

                except json.JSONDecodeError:
                    await self.send_error(websocket, "Invalid JSON")

        except WebSocketDisconnect:
            if player_id:
                await self._handle_disconnect(player_id)

    async def _handle_disconnect(self, player_id: str) -> None:
        """Handle a player disconnection."""
        # Remove from connections
        if player_id in self._connections:
            del self._connections[player_id]

        # Remove from matchmaking queue
        matchmaking = get_matchmaking()
        matchmaking.remove_player(player_id)

        # Mark as disconnected in game
        game_id = matchmaking.get_player_game(player_id)
        game_type = matchmaking.get_player_game_type(player_id)

        if game_id and game_type:
            if game_type == "hangman":
                manager = get_hangman_manager()
                game = manager.get_game(game_id)
                if game:
                    game.remove_player(player_id)

        matchmaking.remove_player_from_game(player_id)

    async def send_to_player(self, player_id: str, message: ServerMessage) -> None:
        """Send a message to a specific player."""
        websocket = self._connections.get(player_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message.to_dict()))
            except Exception:
                pass  # Connection might be closed

    async def send_to_websocket(self, websocket: WebSocket, message: ServerMessage) -> None:
        """Send a message to a specific websocket."""
        try:
            await websocket.send_text(json.dumps(message.to_dict()))
        except Exception:
            pass

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

    async def broadcast_to_queue(self, message: ServerMessage) -> None:
        """Broadcast a message to all players in the matchmaking queue."""
        matchmaking = get_matchmaking()
        for player in matchmaking.queued_players:
            await self.send_to_player(player.id, message)

    async def send_error(self, websocket: WebSocket, error_message: str) -> None:
        """Send an error message to a websocket."""
        await self.send_to_websocket(websocket, ErrorMessage(message=error_message))


# Global singleton instance
_ws_handler: WebSocketHandler | None = None


def get_ws_handler() -> WebSocketHandler:
    """Get the global WebSocket handler instance."""
    global _ws_handler
    if _ws_handler is None:
        _ws_handler = WebSocketHandler()
    return _ws_handler
