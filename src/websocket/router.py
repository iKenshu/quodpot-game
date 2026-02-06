"""Game router for handling multiple game types."""

from typing import Any

from fastapi import WebSocket

from ..config import (
    MATCHMAKING_TIMEOUT_SECONDS,
    MAX_PLAYERS_PER_GAME,
    MIN_PLAYERS_TO_START,
)
from ..games.hangman.events import HangmanEventProcessor
from ..games.hangman.manager import get_hangman_manager
from ..games.hangman.messages import GuessMessage
from ..models.messages import (
    ClientMessage,
    JoinedMessage,
    JoinMessage,
    LeaveMessage,
    WaitingMessage,
)
from ..services.matchmaking import get_matchmaking


class GameRouter:
    """Routes messages to the appropriate game-specific event processor."""

    def __init__(self, handler: "WebSocketHandler"):
        self._handler = handler
        self._player_game_types: dict[str, str] = {}
        self._hangman_processor = HangmanEventProcessor(handler)
        self._setup_game_types()

    def _setup_game_types(self) -> None:
        """Register game types with matchmaking."""
        matchmaking = get_matchmaking()
        manager = get_hangman_manager()
        matchmaking.register_game_type(
            game_type="hangman",
            min_players=MIN_PLAYERS_TO_START,
            max_players=MAX_PLAYERS_PER_GAME,
            timeout_seconds=MATCHMAKING_TIMEOUT_SECONDS,
            game_creator=manager.create_game,
            on_game_start=self._on_hangman_game_start,
            joinable_game_finder=manager.find_joinable_game,
        )

    async def _on_hangman_game_start(self, game) -> None:
        """Called when a Hangman game starts."""
        manager = get_hangman_manager()
        manager.start_game(game)
        await self._hangman_processor.on_game_start(game)

    async def process(
        self, websocket: WebSocket, data: dict, player_id: str | None
    ) -> dict[str, Any] | None:
        """Process an incoming message and route to appropriate handler."""
        message = ClientMessage.parse(data)

        if message is None:
            msg_type = data.get("type")

            if msg_type == "guess" and player_id:
                try:
                    guess_msg = GuessMessage(**data)
                    game_type = self._player_game_types.get(player_id, "hangman")
                    if game_type == "hangman":
                        matchmaking = get_matchmaking()
                        await self._hangman_processor.handle_guess(
                            player_id, guess_msg, matchmaking
                        )
                    return None
                except Exception:
                    pass

            await self._handler.send_error(websocket, "Unknown message type")
            return None

        if isinstance(message, JoinMessage):
            return await self._handle_join(websocket, message)

        elif isinstance(message, LeaveMessage):
            if player_id:
                await self._handle_leave(player_id)

        return None

    async def _handle_join(
        self, websocket: WebSocket, message: JoinMessage
    ) -> dict[str, Any]:
        """Handle a player joining a game."""
        game_type = message.game_type

        matchmaking = get_matchmaking()

        if game_type == "hangman":
            player, game, late_join = await self._hangman_processor.handle_join(
                websocket, message.player_name, matchmaking
            )

            self._player_game_types[player.id] = "hangman"

            if not late_join:
                await self._handler.send_to_websocket(
                    websocket,
                    JoinedMessage(
                        player_id=player.id,
                        game_id=game.id if game else "",
                        player_name=player.name,
                    ),
                )

                if not game:
                    queue_size = matchmaking.get_queue_size("hangman")
                    await self._handler.send_to_websocket(
                        websocket,
                        WaitingMessage(
                            players_in_queue=queue_size,
                            message=f"Esperando jugadores... ({queue_size} en cola)",
                        ),
                    )

                    for queued_player in matchmaking.get_queued_players("hangman"):
                        if queued_player.id != player.id:
                            await self._handler.send_to_player(
                                queued_player.id,
                                WaitingMessage(
                                    players_in_queue=queue_size,
                                    message=f"Esperando jugadores... ({queue_size} en cola)",
                                ),
                            )

            return {"player_id": player.id}

        await self._handler.send_error(websocket, f"Unknown game type: {game_type}")
        return None

    async def _handle_leave(self, player_id: str) -> None:
        """Handle a player leaving."""
        matchmaking = get_matchmaking()
        game_type = self._player_game_types.get(player_id, "hangman")

        matchmaking.remove_player(player_id)

        if game_type == "hangman":
            await self._hangman_processor.handle_leave(player_id, matchmaking)

        matchmaking.remove_player_from_game(player_id)
        if player_id in self._player_game_types:
            del self._player_game_types[player_id]
