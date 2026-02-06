"""WebSocket event processing."""

from typing import TYPE_CHECKING, Any
from fastapi import WebSocket

from ..models.game import Player, Game, GameStatus
from ..models.messages import (
    ClientMessage,
    JoinMessage,
    GuessMessage,
    LeaveMessage,
    JoinedMessage,
    WaitingMessage,
    GameStartMessage,
    StationUpdateMessage,
    CorrectGuessMessage,
    WrongGuessMessage,
    StationCompleteMessage,
    StationFailedMessage,
    PlayerProgressMessage,
    PlayerJoinedMessage,
    GameOverMessage,
    ErrorMessage,
    StationStatusMessage,
)
from ..services.matchmaking import get_matchmaking
from ..services.game_manager import get_game_manager
from ..config import TOTAL_STATIONS

if TYPE_CHECKING:
    from .handler import WebSocketHandler


class EventProcessor:
    """Processes WebSocket events from clients."""

    def __init__(self, handler: "WebSocketHandler"):
        self._handler = handler
        self._setup_matchmaking_callback()

    def _setup_matchmaking_callback(self) -> None:
        """Set up the matchmaking callback for game starts."""
        matchmaking = get_matchmaking()
        matchmaking.set_game_start_callback(self._on_game_start)

    def _get_station_status(self, game: Game) -> dict[int, list[str]]:
        """Get the distribution of players across stations."""
        stations: dict[int, list[str]] = {}
        for i in range(1, TOTAL_STATIONS + 1):
            stations[i] = []

        for player in game.connected_players:
            station = player.current_station
            if station in stations:
                stations[station].append(player.name)

        return stations

    async def _broadcast_station_status(self, game: Game) -> None:
        """Broadcast the current station status to all players in a game."""
        stations = self._get_station_status(game)
        await self._handler.broadcast_to_game(
            game,
            StationStatusMessage(stations=stations),
        )

    async def process(
        self, websocket: WebSocket, data: dict, player_id: str | None
    ) -> dict[str, Any] | None:
        """Process an incoming message."""
        message = ClientMessage.parse(data)

        if message is None:
            await self._handler.send_error(websocket, "Unknown message type")
            return None

        if isinstance(message, JoinMessage):
            return await self._handle_join(websocket, message)

        elif isinstance(message, GuessMessage):
            if player_id is None:
                await self._handler.send_error(websocket, "Not joined to a game")
                return None
            await self._handle_guess(player_id, message)

        elif isinstance(message, LeaveMessage):
            if player_id:
                await self._handle_leave(player_id)

        return None

    async def _handle_join(
        self, websocket: WebSocket, message: JoinMessage
    ) -> dict[str, Any]:
        """Handle a player joining."""
        player = Player.create(message.player_name, websocket)

        matchmaking = get_matchmaking()
        game, late_join = await matchmaking.add_player(player)

        if game and late_join:
            await self._handle_late_join(player, game)
        elif game:
            await self._handler.send_to_websocket(
                websocket,
                JoinedMessage(
                    player_id=player.id,
                    game_id=game.id,
                    player_name=player.name,
                ),
            )
        else:
            await self._handler.send_to_websocket(
                websocket,
                JoinedMessage(
                    player_id=player.id,
                    game_id="",
                    player_name=player.name,
                ),
            )
            await self._handler.send_to_websocket(
                websocket,
                WaitingMessage(
                    players_in_queue=matchmaking.queue_size,
                    message=f"Esperando jugadores... ({matchmaking.queue_size} en cola)",
                ),
            )

            await self._handler.broadcast_to_queue(
                WaitingMessage(
                    players_in_queue=matchmaking.queue_size,
                    message=f"Esperando jugadores... ({matchmaking.queue_size} en cola)",
                )
            )

        return {"player_id": player.id}

    async def _handle_late_join(self, player: Player, game: Game) -> None:
        """Handle a player late-joining an active game."""
        game_manager = get_game_manager()

        await self._handler.send_to_websocket(
            player.websocket,
            JoinedMessage(
                player_id=player.id,
                game_id=game.id,
                player_name=player.name,
            ),
        )

        players_info = [
            {"id": p.id, "name": p.name}
            for p in game.connected_players
        ]
        await self._handler.send_to_websocket(
            player.websocket,
            GameStartMessage(
                players=players_info,
                total_stations=TOTAL_STATIONS,
            ),
        )

        station_info = game_manager.get_player_station_info(player)
        await self._handler.send_to_websocket(
            player.websocket,
            StationUpdateMessage(**station_info),
        )

        await self._handler.broadcast_to_game_except(
            game,
            PlayerJoinedMessage(
                player_id=player.id,
                player_name=player.name,
                station=player.current_station,
            ),
            except_player_id=player.id,
        )

        await self._broadcast_station_status(game)

    async def _handle_guess(self, player_id: str, message: GuessMessage) -> None:
        """Handle a letter guess."""
        matchmaking = get_matchmaking()
        game_manager = get_game_manager()

        game_id = matchmaking.get_player_game(player_id)
        if not game_id:
            return

        game = game_manager.get_game(game_id)
        if not game or game.status != GameStatus.PLAYING:
            return

        player = game.get_player(player_id)
        if not player:
            return

        # Process the guess
        result = game_manager.process_guess(game, player, message.letter)

        if "error" in result:
            await self._handler.send_to_player(
                player_id, ErrorMessage(message=result["error"])
            )
            return

        # Send result to player
        if result["correct"]:
            await self._handler.send_to_player(
                player_id,
                CorrectGuessMessage(
                    letter=result["letter"],
                    revealed=result["revealed"],
                ),
            )
        else:
            await self._handler.send_to_player(
                player_id,
                WrongGuessMessage(
                    letter=result["letter"],
                    attempts_left=result["attempts_left"],
                ),
            )

        # Handle station completion or failure
        if result["station_complete"]:
            await self._handler.send_to_player(
                player_id,
                StationCompleteMessage(
                    station=player.current_station - 1,  # Previous station completed
                    word=result["word"],
                ),
            )

            if result["game_won"]:
                # Broadcast game over
                await self._handler.broadcast_to_game(
                    game,
                    GameOverMessage(
                        winner_id=player.id,
                        winner_name=player.name,
                        words=game.words,
                    ),
                )
            else:
                # Send new station update
                station_info = game_manager.get_player_station_info(player)
                await self._handler.send_to_player(
                    player_id,
                    StationUpdateMessage(**station_info),
                )

                # Broadcast progress to others
                await self._handler.broadcast_to_game_except(
                    game,
                    PlayerProgressMessage(
                        player_id=player.id,
                        player_name=player.name,
                        station=player.current_station,
                    ),
                    except_player_id=player_id,
                )

                # Broadcast updated station status
                await self._broadcast_station_status(game)

        elif result["station_failed"]:
            await self._handler.send_to_player(
                player_id,
                StationFailedMessage(
                    reset_to=1,
                    word=result["word"],
                ),
            )

            # Send new station 1 update
            station_info = game_manager.get_player_station_info(player)
            await self._handler.send_to_player(
                player_id,
                StationUpdateMessage(**station_info),
            )

            # Broadcast progress (reset) to others
            await self._handler.broadcast_to_game_except(
                game,
                PlayerProgressMessage(
                    player_id=player.id,
                    player_name=player.name,
                    station=1,
                ),
                except_player_id=player_id,
            )

            # Broadcast updated station status
            await self._broadcast_station_status(game)

    async def _handle_leave(self, player_id: str) -> None:
        """Handle a player leaving."""
        matchmaking = get_matchmaking()
        game_manager = get_game_manager()

        # Remove from queue
        matchmaking.remove_player(player_id)

        # Remove from game
        game_id = matchmaking.get_player_game(player_id)
        if game_id:
            game = game_manager.get_game(game_id)
            if game:
                game.remove_player(player_id)
                # Broadcast updated station status to remaining players
                if game.connected_players:
                    await self._broadcast_station_status(game)
            matchmaking.remove_player_from_game(player_id)

    async def _on_game_start(self, game: Game) -> None:
        """Called when a game starts from matchmaking."""
        # Send game start to all players
        players_info = [
            {"id": p.id, "name": p.name}
            for p in game.connected_players
        ]

        await self._handler.broadcast_to_game(
            game,
            GameStartMessage(
                players=players_info,
                total_stations=TOTAL_STATIONS,
            ),
        )

        # Send initial station update to each player
        game_manager = get_game_manager()
        for player in game.connected_players:
            station_info = game_manager.get_player_station_info(player)
            await self._handler.send_to_player(
                player.id,
                StationUpdateMessage(**station_info),
            )

        # Broadcast initial station status
        await self._broadcast_station_status(game)
