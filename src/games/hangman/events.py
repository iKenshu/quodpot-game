from typing import Any

from fastapi import WebSocket

from config import TOTAL_STATIONS
from models.base import GameStatus
from models.messages import ErrorMessage

from .manager import get_hangman_manager
from .messages import (
    CorrectGuessMessage,
    GameOverMessage,
    GameStartMessage,
    GuessMessage,
    PlayerJoinedMessage,
    PlayerProgressMessage,
    StationCompleteMessage,
    StationFailedMessage,
    StationStatusMessage,
    StationUpdateMessage,
    WrongGuessMessage,
)
from .models import HangmanGame, HangmanPlayer


class HangmanEventProcessor:
    """Processes Hangman-specific WebSocket events."""

    def __init__(self, handler: "WebSocketHandler"):
        self._handler = handler

    def _get_station_status(self, game: HangmanGame) -> dict[int, list[str]]:
        """Get the distribution of players across stations."""
        stations: dict[int, list[str]] = {}
        for i in range(1, TOTAL_STATIONS + 1):
            stations[i] = []

        for player in game.connected_players:
            station = player.current_station
            if station in stations:
                stations[station].append(player.name)

        return stations

    async def _broadcast_station_status(self, game: HangmanGame) -> None:
        """Broadcast the current station status to all players in a game."""
        stations = self._get_station_status(game)
        await self._handler.broadcast_to_game(
            game,
            StationStatusMessage(stations=stations),
        )

    async def handle_join(
        self, websocket: WebSocket, player_name: str, matchmaking
    ) -> tuple[HangmanPlayer, HangmanGame | None, bool]:
        """
        Handle a player joining Hangman.
        Returns (player, game, is_late_join).
        """
        player = HangmanPlayer.create(player_name, websocket)
        game, late_join = await matchmaking.add_player(player, "hangman")

        if game and late_join:
            manager = get_hangman_manager()
            manager.add_player_to_active_game(game, player)
            await self._handle_late_join(player, game)

        return player, game, late_join

    async def _handle_late_join(self, player: HangmanPlayer, game: HangmanGame) -> None:
        """Handle a player late-joining an active game."""
        manager = get_hangman_manager()

        players_info = [{"id": p.id, "name": p.name} for p in game.connected_players]
        await self._handler.send_to_websocket(
            player.websocket,
            GameStartMessage(
                players=players_info,
                total_stations=TOTAL_STATIONS,
            ),
        )

        station_info = manager.get_player_station_info(player)
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

    async def handle_guess(
        self, player_id: str, message: GuessMessage, matchmaking
    ) -> None:
        """Handle a letter guess."""
        manager = get_hangman_manager()

        game_id = matchmaking.get_player_game(player_id)
        if not game_id:
            return

        game = manager.get_game(game_id)
        if not game or game.status != GameStatus.PLAYING:
            return

        player = game.get_player(player_id)
        if not player:
            return

        result = manager.process_guess(game, player, message.letter)

        if "error" in result:
            await self._handler.send_to_player(
                player_id, ErrorMessage(message=result["error"])
            )
            return

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

        if result["station_complete"]:
            await self._handler.send_to_player(
                player_id,
                StationCompleteMessage(
                    station=player.current_station - 1,  # Previous station completed
                    word=result["word"],
                ),
            )

            if result["game_won"]:
                await self._handler.broadcast_to_game(
                    game,
                    GameOverMessage(
                        winner_id=player.id,
                        winner_name=player.name,
                        words=game.words,
                    ),
                )
            else:
                station_info = manager.get_player_station_info(player)
                await self._handler.send_to_player(
                    player_id,
                    StationUpdateMessage(**station_info),
                )

                await self._handler.broadcast_to_game_except(
                    game,
                    PlayerProgressMessage(
                        player_id=player.id,
                        player_name=player.name,
                        station=player.current_station,
                    ),
                    except_player_id=player_id,
                )

                await self._broadcast_station_status(game)

        elif result["station_failed"]:
            await self._handler.send_to_player(
                player_id,
                StationFailedMessage(
                    reset_to=1,
                    word=result["word"],
                ),
            )

            station_info = manager.get_player_station_info(player)
            await self._handler.send_to_player(
                player_id,
                StationUpdateMessage(**station_info),
            )

            await self._handler.broadcast_to_game_except(
                game,
                PlayerProgressMessage(
                    player_id=player.id,
                    player_name=player.name,
                    station=1,
                ),
                except_player_id=player_id,
            )

            await self._broadcast_station_status(game)

    async def on_game_start(self, game: HangmanGame) -> None:
        """Called when a Hangman game starts from matchmaking."""
        manager = get_hangman_manager()

        players_info = [{"id": p.id, "name": p.name} for p in game.connected_players]

        await self._handler.broadcast_to_game(
            game,
            GameStartMessage(
                players=players_info,
                total_stations=TOTAL_STATIONS,
            ),
        )

        for player in game.connected_players:
            station_info = manager.get_player_station_info(player)
            await self._handler.send_to_player(
                player.id,
                StationUpdateMessage(**station_info),
            )

        await self._broadcast_station_status(game)

    async def handle_leave(self, player_id: str, matchmaking) -> None:
        """Handle a Hangman player leaving."""
        manager = get_hangman_manager()

        game_id = matchmaking.get_player_game(player_id)
        if game_id:
            game = manager.get_game(game_id)
            if game:
                game.remove_player(player_id)
                if game.connected_players:
                    await self._broadcast_station_status(game)
                    await self._broadcast_station_status(game)
