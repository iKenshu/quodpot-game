"""Game router for handling multiple game types."""

import logging
from typing import Any

from fastapi import WebSocket

from ..config import (
    GAME_TYPE_HANGMAN,
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

logger = logging.getLogger(__name__)


class GameRouter:
    """Routes messages to the appropriate game-specific event processor.

    This class handles routing of incoming WebSocket messages to the appropriate
    game-specific processors, manages player-game associations, and coordinates
    matchmaking operations.
    """

    def __init__(self, handler: "WebSocketHandler"):
        self._handler = handler
        self._player_game_types: dict[str, str] = {}
        self._hangman_processor = HangmanEventProcessor(handler)
        self._matchmaking = get_matchmaking()
        self._setup_game_types()

    def _setup_game_types(self) -> None:
        """Register game types with matchmaking service."""
        manager = get_hangman_manager()
        self._matchmaking.register_game_type(
            game_type=GAME_TYPE_HANGMAN,
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
        """Process an incoming message and route to appropriate handler.

        Args:
            websocket: The WebSocket connection
            data: Raw message data from the client
            player_id: Optional player ID if already authenticated

        Returns:
            A dict with player_id for join messages, None otherwise
        """
        message = ClientMessage.parse(data)

        if message is None:
            return await self._handle_unparsed_message(websocket, data, player_id)

        if isinstance(message, JoinMessage):
            return await self._handle_join(websocket, message)

        if isinstance(message, LeaveMessage) and player_id:
            await self._handle_leave(player_id)

        return None

    async def _handle_unparsed_message(
        self, websocket: WebSocket, data: dict, player_id: str | None
    ) -> None:
        """Handle messages that don't match the standard ClientMessage format."""
        msg_type = data.get("type")

        if msg_type == "guess" and player_id:
            try:
                guess_msg = GuessMessage(**data)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid guess message from player {player_id}: {e}",
                    extra={"player_id": player_id, "data": data},
                )
                await self._handler.send_error(websocket, "Invalid guess format")
                return None

            game_type = self._player_game_types.get(player_id, GAME_TYPE_HANGMAN)
            if game_type == GAME_TYPE_HANGMAN:
                await self._hangman_processor.handle_guess(
                    player_id, guess_msg, self._matchmaking
                )
            return None

        await self._handler.send_error(websocket, "Unknown message type")
        return None

    async def _handle_join(
        self, websocket: WebSocket, message: JoinMessage
    ) -> dict[str, Any] | None:
        """Handle a player joining a game.

        Args:
            websocket: The WebSocket connection
            message: The join message from the client

        Returns:
            A dict containing the player_id, or None if the game type is invalid
        """
        game_type = message.game_type

        if game_type != GAME_TYPE_HANGMAN:
            await self._handler.send_error(websocket, f"Unknown game type: {game_type}")
            logger.warning(
                f"Attempted join with unknown game type: {game_type}",
                extra={"game_type": game_type, "player_name": message.player_name},
            )
            return None

        player, game, late_join = await self._hangman_processor.handle_join(
            websocket, message.player_name, self._matchmaking
        )

        self._player_game_types[player.id] = GAME_TYPE_HANGMAN

        if not late_join:
            await self._send_joined_message(websocket, player, game)

            if not game:
                await self._broadcast_waiting_status(player.id)

        logger.info(
            f"Player {player.name} joined game",
            extra={
                "player_id": player.id,
                "game_id": game.id if game else None,
                "late_join": late_join,
            },
        )

        return {"player_id": player.id}

    async def _send_joined_message(self, websocket: WebSocket, player, game) -> None:
        """Send the joined confirmation message to a player."""
        await self._handler.send_to_websocket(
            websocket,
            JoinedMessage(
                player_id=player.id,
                game_id=game.id if game else "",
                player_name=player.name,
            ),
        )

    async def _broadcast_waiting_status(self, new_player_id: str) -> None:
        """Broadcast waiting status to all players in queue.

        Args:
            new_player_id: The ID of the player who just joined the queue
        """
        queue_size = self._matchmaking.get_queue_size(GAME_TYPE_HANGMAN)
        waiting_msg = WaitingMessage(
            players_in_queue=queue_size,
            message=f"Esperando jugadores... ({queue_size} en cola)",
        )

        for queued_player in self._matchmaking.get_queued_players(GAME_TYPE_HANGMAN):
            await self._handler.send_to_player(queued_player.id, waiting_msg)

    async def _handle_leave(self, player_id: str) -> None:
        """Handle a player leaving the game.

        Performs cleanup: removes from matchmaking queue/game and
        notifies game-specific processor for additional handling.

        Args:
            player_id: The ID of the player leaving
        """
        game_type = self._player_game_types.get(player_id, GAME_TYPE_HANGMAN)

        self._matchmaking.remove_player(player_id)
        self._matchmaking.remove_player_from_game(player_id)

        if game_type == GAME_TYPE_HANGMAN:
            await self._hangman_processor.handle_leave(player_id, self._matchmaking)

        self._player_game_types.pop(player_id, None)

        logger.info(
            "Player left game", extra={"player_id": player_id, "game_type": game_type}
        )
