import asyncio
import logging
from typing import Optional

from .agents.agent import RLAgent
from .directions import DIRECTIONS
from .game_board import GameBoard
from .models import CellState, ShipType, get_fleet, get_ship_name
from .websocket import GameWebSocketServer

logger = logging.getLogger(__name__)


class GameEngine:
    """
    Orchestrates a full game of Battleship.

    Modes
    -----
    automated  : Both fleets placed randomly; agent uses stub random moves.
                 Runs to completion without user input (useful for RL training).
    interactive: Human places their own ships and fires manually;
                 agent's fleet is placed randomly and moves come from WS or stub.

    WebSocket
    ---------
    A GameWebSocketServer runs as a background asyncio task.
    After every move the full game_state is broadcast to all observers.
    If an RL agent connects over WebSocket the game awaits its move commands;
    otherwise the local RLAgent stub makes random moves.
    Pass --no-ws at the CLI to skip starting the server.
    """

    def __init__(
        self,
        mode: str = "automated",
        ws_host: str = "localhost",
        ws_port: int = 8765,
        enable_ws: bool = True,
    ) -> None:
        self.mode = mode
        self.enable_ws = enable_ws

        self.player_board = GameBoard()
        self.agent_board = GameBoard()

        self.ws_server = (
            GameWebSocketServer(host=ws_host, port=ws_port) if enable_ws else None
        )
        self.rl_agent = RLAgent()

        self._turn: int = 0
        self._current_player: str = "player"
        self._game_over: bool = False
        self._winner: Optional[str] = None
        self._last_move: Optional[dict] = None

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self) -> None:
        server_task: Optional[asyncio.Task] = None
        if self.ws_server:
            server_task = asyncio.create_task(self.ws_server.start())
            # Brief yield so the server socket is bound before setup begins.
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
        if self.mode == "interactive":
            await self._setup_interactive()
        else:
            await self._setup_automated()

    async def _setup_automated(self) -> None:
        self.player_board.place_fleet()
        self.agent_board.place_fleet()
        logger.info("Automated mode: fleets placed via pluggable placement strategy")

    async def _setup_interactive(self) -> None:
        print("\n=== BATTLESHIP ===")
        print("Place your ships. Format: <coordinate> <direction>")
        print("  Example: A1 right  |  B5 down  |  J10 up")
        directions = ", ".join(DIRECTIONS.keys())
        print(f"  Directions: {directions}\n")

        for ship_type in get_fleet():
            await self._prompt_ship_placement(ship_type)

        print("\nYour fleet is placed. Agent is placing its fleet...")
        self.agent_board.place_fleet()
        print("Ready! Game starting.\n")

    async def _prompt_ship_placement(self, ship_type: ShipType) -> None:
        loop = asyncio.get_event_loop()
        name = get_ship_name(ship_type)

        while True:
            self.player_board.display(fog_of_war=False, label="Your Board")
            prompt = f"Place your {name} — enter coordinate and direction: "
            raw: str = await loop.run_in_executor(None, input, prompt)
            raw = raw.strip()
            parts = raw.split()
            if len(parts) != 2:
                print(
                    "  Invalid input. Use format: <coordinate> <direction>  (e.g. A1 right)\n"
                )
                continue
            coord, direction = parts[0], parts[1].lower()
            try:
                _ = self.player_board.place_ship_from_str(ship_type, coord, direction)
                print(f"  {name} placed.\n")
                return
            except ValueError as e:
                print(f"  Error: {e}\n")

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

            self._display_boards()

            if self.ws_server:
                state = self._build_state_dict()
                await self.ws_server.broadcast_state(state)
                if self.ws_server.agent_connected:
                    await self.ws_server.send_to_agent(self._build_agent_view_dict())

            if self._check_win_condition():
                if self.ws_server:
                    await self.ws_server.broadcast_state(self._build_game_over_dict())
                break

            self._current_player = (
                "rl_agent" if self._current_player == "player" else "player"
            )
            await asyncio.sleep(0)  # yield to event loop

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------

    async def _take_player_turn(self) -> None:
        if self.mode == "automated":
            await self._player_random_shot()
        else:
            await self._player_interactive_shot()

    async def _player_random_shot(self) -> None:
        import random

        unhit = self.agent_board.get_unhit_cells()
        row, col = random.choice(unhit)
        await self._fire_on_agent_board(row, col)

    async def _player_interactive_shot(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            raw: str = await loop.run_in_executor(None, input, "Your shot (e.g. B5): ")
            raw = raw.strip()
            try:
                row, col = GameBoard.parse_coordinate(raw)
                await self._fire_on_agent_board(row, col)
                return
            except ValueError as e:
                print(f"  Invalid: {e}")

    async def _fire_on_agent_board(self, row: int, col: int) -> None:
        coord = GameBoard.format_coordinate(row, col)
        try:
            state, ship = self.agent_board.receive_shot(row, col)
        except ValueError as e:
            print(f"  {e}")
            return

        sunk_name = ship.ship_type.name if (ship and ship.is_sunk) else None
        result_str = "HIT" if state is CellState.HIT else "MISS"
        msg = f"  Player fires {coord}: {result_str}"
        if sunk_name:
            msg += f" — {sunk_name} sunk!"
        print(msg)

        self._last_move = {
            "player": "player",
            "coordinate": coord,
            "result": result_str,
            "ship_sunk": sunk_name,
        }

    async def _take_agent_turn(self) -> None:
        if self.ws_server and self.ws_server.agent_connected:
            # Real agent sends move over WebSocket; await it.
            coord = await self.ws_server.wait_for_agent_move()
        else:
            # Use local stub for random play.
            board_state = self._build_state_dict()
            coord = self.rl_agent.select_move(board_state)

        try:
            row, col = GameBoard.parse_coordinate(coord)
        except ValueError as e:
            logger.warning("Agent sent invalid coordinate '%s': %s", coord, e)
            return

        try:
            state, ship = self.player_board.receive_shot(row, col)
        except ValueError as e:
            logger.warning("Agent double-fired at %s: %s", coord, e)
            return

        sunk_name = ship.ship_type.name if (ship and ship.is_sunk) else None
        result_str = "HIT" if state is CellState.HIT else "MISS"
        msg = f"  Agent fires {coord}: {result_str}"
        if sunk_name:
            msg += f" — {sunk_name} sunk!"
        print(msg)

        self.rl_agent.receive_result(coord, result_str, sunk_name)

        if self.ws_server and self.ws_server.agent_connected:
            await self.ws_server.send_to_agent(
                {
                    "type": "move_ack",
                    "coordinate": coord,
                    "result": result_str,
                    "ship_sunk": sunk_name,
                    "game_over": False,
                }
            )

        self._last_move = {
            "player": "rl_agent",
            "coordinate": coord,
            "result": result_str,
            "ship_sunk": sunk_name,
        }

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
            self._winner = "rl_agent"
            return True
        return False

    # ------------------------------------------------------------------
    # State serialisation
    # ------------------------------------------------------------------

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
                # Observers see agent board with fog (no ship positions unless hit)
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
                "rl_agent": {
                    "ships_sunk": self.player_board.ships_sunk_count(),
                    "cells_hit": self.player_board.cells_hit_count(),
                },
            },
            "last_move": self._last_move,
        }

    def _build_agent_view_dict(self) -> dict:
        """Fog-of-war observation sent exclusively to the connected RL agent."""
        return {
            "type": "agent_view",
            "turn": self._turn,
            # Enemy (player) board: agent only sees hits/misses, not ship positions
            "enemy_board_fog": self.player_board.board_as_matrix(fog_of_war=True),
            # Own board: agent sees where it was hit
            "your_board_fog": self.agent_board.board_as_matrix(fog_of_war=False),
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
                "rl_agent": {
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
        self.player_board.display(fog_of_war=False, label="Your Board")
        self.agent_board.display(fog_of_war=True, label="Agent's Board (your shots)")

    def _display_game_over(self) -> None:
        print("\n" + "=" * 40)
        print("GAME OVER")
        winner_label = "You" if self._winner == "player" else "The RL Agent"
        print(f"Winner: {winner_label}")
        print(f"Total turns: {self._turn}")
        print(
            f"Your score    — ships sunk: {self.agent_board.ships_sunk_count()}, "
            f"cells hit: {self.agent_board.cells_hit_count()}"
        )
        print(
            f"Agent's score — ships sunk: {self.player_board.ships_sunk_count()}, "
            f"cells hit: {self.player_board.cells_hit_count()}"
        )
        print("=" * 40)
