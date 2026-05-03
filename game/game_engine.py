import asyncio
import random
from typing import Optional

from .agents.base_agent import BaseAgent
from .coordinate_methods import format_coordinate, parse_coordinate
from .game_board import GameBoard
from .logger import GameLogger
from .models import CellState, get_fleet, get_ship_size
from .websocket import GameWebSocketServer


class GameEngine:
    """
    Orchestrates a full game of Battleship.

    The game-side agent always runs in-process and is passed in at construction.
    The player is either a random stub or a WebSocket-connected human, controlled
    by the `player_type` argument.

    WebSocket
    ---------
    A GameWebSocketServer runs as a background asyncio task.
    After every move the full game_state is broadcast to all observers.
    Pass enable_ws=False to skip starting the server.
    """

    def __init__(
        self,
        agent: BaseAgent,
        player_type: str = "random",
        player_placement: str = "random",
        ws_host: str = "localhost",
        ws_port: int = 8765,
        enable_ws: bool = True,
        headless: bool = False,
    ) -> None:
        self.agent = agent
        self.player_type = player_type
        self.player_placement = player_placement
        self.enable_ws = enable_ws
        self.headless = headless

        self.reset()

        self.ws_server = (
            GameWebSocketServer(host=ws_host, port=ws_port) if enable_ws else None
        )

    def reset(self) -> None:
        self.player_board = GameBoard()
        self.agent_board = GameBoard()
        self._turn = 0
        self._current_player = "player"
        self._game_over = False
        self._winner = None
        self._last_move = None
        self.agent.reset()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self) -> None:
        server_task: Optional[asyncio.Task] = None
        if self.ws_server:
            server_task = asyncio.create_task(self.ws_server.start())
            await asyncio.sleep(0)

        try:
            await self._setup()
            await self._game_loop()
        finally:
            if self.ws_server:
                await self.ws_server.stop()
            if server_task:
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass

        self._display_game_over()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    async def _setup(self) -> None:
        self.agent.place_fleet(self.agent_board)

        if self.player_type == "websocket":
            await self._setup_ws_player()
        else:
            self.player_board.place_fleet()
            GameLogger.info("Setup complete: agent vs random player")

    async def _setup_ws_player(self) -> None:
        assert self.ws_server is not None
        GameLogger.info("Waiting for WebSocket player to connect...")
        while not self.ws_server.player_connected:
            await asyncio.sleep(0.1)
        GameLogger.info("WebSocket player connected")

        if self.player_placement == "manual":
            for ship_type in get_fleet():
                await self.ws_server.send_to_player(
                    {
                        "type": "place_ship",
                        "ship": ship_type.name,
                        "size": get_ship_size(ship_type),
                    }
                )
                while True:
                    msg = await self.ws_server.wait_for_player_placement()
                    try:
                        self.player_board.place_ship_from_str(
                            ship_type, msg["coordinate"], msg["direction"]
                        )
                        await self.ws_server.send_to_player(
                            {"type": "placement_ack", "valid": True}
                        )
                        break
                    except (ValueError, KeyError) as e:
                        await self.ws_server.send_to_player(
                            {"type": "placement_ack", "valid": False, "error": str(e)}
                        )
        else:
            self.player_board.place_fleet()

        await self.ws_server.send_to_player(
            {
                "type": "game_start",
                "your_board": self.player_board.board_as_matrix(),
            }
        )
        GameLogger.info("Setup complete: agent vs WebSocket player")

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    async def _game_loop(self) -> None:
        while not self._game_over:
            self._turn += 1

            if self._current_player == "player":
                await self._take_player_turn()
            else:
                await self._take_agent_turn()

            if not self.headless:
                self._display_boards()

            if self.ws_server:
                await self.ws_server.broadcast_state(self._build_state_dict())

            if self._check_win_condition():
                if self.ws_server:
                    await self.ws_server.broadcast_state(self._build_game_over_dict())
                break

            self._current_player = (
                "agent" if self._current_player == "player" else "player"
            )
            await asyncio.sleep(0)

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------

    async def _take_player_turn(self) -> None:
        if self.player_type == "websocket":
            assert self.ws_server is not None
            await self.ws_server.send_to_player(self._build_player_view())
            coord = await self.ws_server.wait_for_player_move()
            try:
                row, col = parse_coordinate(coord)
            except ValueError as e:
                GameLogger.warn("Player sent invalid coordinate '%s': %s", coord, e)
                return
            await self._fire_on_agent_board(row, col)
            if self.ws_server and self._last_move:
                await self.ws_server.send_to_player(
                    {
                        "type": "move_ack",
                        "coordinate": self._last_move["coordinate"],
                        "result": self._last_move["result"],
                        "ship_sunk": self._last_move["ship_sunk"],
                        "game_over": self._game_over,
                    }
                )
        else:
            unhit = self.agent_board.get_unhit_cells()
            row, col = random.choice(unhit)
            await self._fire_on_agent_board(row, col)

    async def _fire_on_agent_board(self, row: int, col: int) -> None:
        coord = format_coordinate(row, col)
        try:
            state, ship = self.agent_board.receive_shot(row, col)
        except ValueError as e:
            GameLogger.warn("Player fired invalid cell: %s", e)
            return

        sunk_name = ship.ship_type.name if (ship and ship.is_sunk) else None
        result_str = "HIT" if state is CellState.HIT else "MISS"
        msg = f"Player fires {coord}: {result_str}"
        if sunk_name:
            msg += f" — {sunk_name} sunk!"
        GameLogger.info(msg)

        if ship and ship.is_sunk and self.ws_server:
            await self.ws_server.broadcast_state(
                {
                    "type": "ship_sunk",
                    "attacker": "player",
                    "ship": sunk_name,
                    "turn": self._turn,
                }
            )

        self._last_move = {
            "player": "player",
            "coordinate": coord,
            "result": result_str,
            "ship_sunk": sunk_name,
        }

    async def _take_agent_turn(self) -> None:
        obs = self._build_agent_obs()
        coord = self.agent.select_move(obs)

        try:
            row, col = parse_coordinate(coord)
        except ValueError as e:
            GameLogger.warn("Agent sent invalid coordinate '%s': %s", coord, e)
            return

        try:
            state, ship = self.player_board.receive_shot(row, col)
        except ValueError as e:
            GameLogger.warn("Agent double-fired at %s: %s", coord, e)
            return

        sunk_name = ship.ship_type.name if (ship and ship.is_sunk) else None
        result_str = "HIT" if state is CellState.HIT else "MISS"
        msg = f"Agent fires {coord}: {result_str}"
        if sunk_name:
            msg += f" — {sunk_name} sunk!"
        GameLogger.info(msg)

        self.agent.receive_result(coord, result_str, sunk_name)

        if ship and ship.is_sunk and self.ws_server:
            await self.ws_server.broadcast_state(
                {
                    "type": "ship_sunk",
                    "attacker": "agent",
                    "ship": sunk_name,
                    "turn": self._turn,
                }
            )

        self._last_move = {
            "player": "agent",
            "coordinate": coord,
            "result": result_str,
            "ship_sunk": sunk_name,
        }

    @property
    def turn(self) -> int:
        return self._turn

    # ------------------------------------------------------------------
    # Win condition
    # ------------------------------------------------------------------

    def _check_win_condition(self) -> bool:
        if self.agent_board.all_ships_sunk():
            self._game_over = True
            self._winner = "player"
            return True
        if self.player_board.all_ships_sunk():
            self._game_over = True
            self._winner = "agent"
            return True
        return False

    @property
    def game_over(self) -> bool:
        return self._game_over

    @property
    def winner(self) -> Optional[str]:
        return self._winner

    # ------------------------------------------------------------------
    # State serialization
    # ------------------------------------------------------------------

    def _build_agent_obs(self) -> dict:
        return {
            "enemy_board": self.player_board.board_as_matrix(fog_of_war=True),
            "your_board": self.agent_board.board_as_matrix(fog_of_war=False),
            "ships_sunk": {
                "by_you": self.player_board.ships_sunk_count(),
                "against_you": self.agent_board.ships_sunk_count(),
            },
            "turn": self._turn,
        }

    def _build_player_view(self) -> dict:
        return {
            "type": "player_view",
            "enemy_board": self.agent_board.board_as_matrix(fog_of_war=True),
            "your_board": self.player_board.board_as_matrix(fog_of_war=False),
            "ships_sunk": {
                "by_you": self.agent_board.ships_sunk_count(),
                "against_you": self.player_board.ships_sunk_count(),
            },
            "turn": self._turn,
        }

    def _build_state_dict(self) -> dict:
        return {
            "type": "game_state",
            "game_id": self.ws_server.game_id if self.ws_server else None,
            "turn": self._turn,
            "current_player": self._current_player,
            "game_over": self._game_over,
            "winner": self._winner,
            "player_board": {
                "cells": self.player_board.board_as_matrix(fog_of_war=False),
                "ships_remaining": len(self.player_board.board.ships)
                - self.player_board.ships_sunk_count(),
                "ships_sunk": self.player_board.ships_sunk_count(),
                "cells_hit": self.player_board.cells_hit_count(),
            },
            "agent_board": {
                "cells": self.agent_board.board_as_matrix(fog_of_war=True),
                "ships_remaining": len(self.agent_board.board.ships)
                - self.agent_board.ships_sunk_count(),
                "ships_sunk": self.agent_board.ships_sunk_count(),
                "cells_hit": self.agent_board.cells_hit_count(),
            },
            "scores": {
                "player": {
                    "ships_sunk": self.agent_board.ships_sunk_count(),
                    "cells_hit": self.agent_board.cells_hit_count(),
                },
                "agent": {
                    "ships_sunk": self.player_board.ships_sunk_count(),
                    "cells_hit": self.player_board.cells_hit_count(),
                },
            },
            "last_move": self._last_move,
        }

    def _build_game_over_dict(self) -> dict:
        return {
            "type": "game_over",
            "winner": self._winner,
            "total_turns": self._turn,
            "scores": {
                "player": {
                    "ships_sunk": self.agent_board.ships_sunk_count(),
                    "cells_hit": self.agent_board.cells_hit_count(),
                },
                "agent": {
                    "ships_sunk": self.player_board.ships_sunk_count(),
                    "cells_hit": self.player_board.cells_hit_count(),
                },
            },
        }

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def _display_boards(self) -> None:
        print(f"\n--- Turn {self._turn} ---")
        self.player_board.display(fog_of_war=False, label="Player's Board")
        self.agent_board.display(
            fog_of_war=True, label="Agent's Board (player's shots)"
        )

    def _display_game_over(self) -> None:
        winner_label = "Player" if self._winner == "player" else "The Agent"

        def _report_score(board: GameBoard, owner: str) -> str:
            return f"  {owner:6s} — sunk: {board.ships_sunk_count()}, hit: {board.cells_hit_count()}"

        gameover_msg = f"GAME OVER — Winner: {winner_label} | Turns: {self._turn}"
        # You report the board of your opponent since that's what you were trying to sink/hit
        player_report = _report_score(self.agent_board, "Player")
        agent_report = _report_score(self.player_board, "Agent")

        print(gameover_msg)
        print(player_report)
        print(agent_report)
        print("-" * len(gameover_msg))

        GameLogger.info(gameover_msg)
        GameLogger.info(player_report)
        GameLogger.info(agent_report)
