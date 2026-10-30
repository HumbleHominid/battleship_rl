from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING, Optional

from .agents.base_agent import BaseAgent
from .coordinate_methods import format_coordinate, parse_coordinate
from .game_board import GameBoard
from .models import FLEET, CellState, get_ship_size

if TYPE_CHECKING:
    from server.ws_session import FastAPIWebSocketAdapter

log = logging.getLogger(__name__)


class GameEngine:
    """
    Orchestrates a full game of Battleship.

    The game-side agent always runs in-process and is passed in at construction.
    The player is either another in-process agent (player_agent) or a human
    connected over WebSocket (ws_server).
    """

    def __init__(
        self,
        agent: BaseAgent,
        player_agent: BaseAgent | None = None,
        ws_server: FastAPIWebSocketAdapter | None = None,
        player_placement: str = "random",
        headless: bool = False,
        log_boards: bool = False,
    ) -> None:
        self.agent = agent
        self.player_agent = player_agent
        self.ws_server = ws_server
        self.player_placement = player_placement
        self.headless = headless
        self.log_boards = log_boards

        self.reset()

    def reset(self) -> None:
        self.player_board = GameBoard(self.log_boards)
        self.agent_board = GameBoard(self.log_boards)
        self._turn = 0
        self._current_player = "player" if random.random() < 0.5 else "agent"
        self._game_over = False
        self._winner = None
        self._last_move = None
        self.agent.reset()
        if self.player_agent:
            self.player_agent.reset()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self) -> None:
        try:
            await self._setup()
            await self._game_loop()
        finally:
            if self.ws_server:
                await self.ws_server.stop()

        self._display_game_over()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    async def _setup(self) -> None:
        self.agent.place_fleet(self.agent_board)

        if self.ws_server:
            await self._setup_ws_player()
        else:
            self.player_board.place_fleet()
            log.info("Setup complete: agent vs agent")

    async def _setup_ws_player(self) -> None:
        assert self.ws_server is not None
        log.info("Waiting for WebSocket player to connect...")
        while not self.ws_server.player_connected:
            await asyncio.sleep(0.1)
        log.info("WebSocket player connected")

        if self.player_placement == "manual":
            for ship_type in FLEET:
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
        log.info("Setup complete: agent vs WebSocket player")

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    async def _send(self, message: dict) -> None:
        if self.ws_server:
            await self.ws_server.send_to_player(message)

    async def _game_loop(self) -> None:
        while not self._game_over:
            self._turn += 1
            self._last_move = None

            if self._current_player == "player":
                await self._take_player_turn()
            else:
                await self._agent_move(
                    self.agent, self._agent_obs(), "agent", self.player_board
                )

            if not self.headless:
                self._display_boards()

            await self._send(self._build_state_dict())

            if self._check_win_condition():
                await self._send(self._build_game_over_dict())
                break

            self._current_player = (
                "agent" if self._current_player == "player" else "player"
            )
            await asyncio.sleep(0)

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------

    async def _take_player_turn(self) -> None:
        if not self.ws_server:
            assert self.player_agent is not None
            await self._agent_move(
                self.player_agent, self._player_view(), "player", self.agent_board
            )
            return

        await self.ws_server.send_to_player(self._player_view())
        coord = await self.ws_server.wait_for_player_move()
        await self._fire("player", self.agent_board, coord)
        self._check_win_condition()
        if self._last_move:
            await self.ws_server.send_to_player(
                {
                    "type": "move_ack",
                    "coordinate": self._last_move["coordinate"],
                    "result": self._last_move["result"],
                    "ship_hit": self._last_move["ship_hit"],
                    "ship_sunk": self._last_move["ship_sunk"],
                    "game_over": self._game_over,
                    "winner": self._winner if self._game_over else None,
                }
            )

    async def _agent_move(
        self, agent: BaseAgent, obs: dict, attacker: str, board: GameBoard
    ) -> None:
        coord = agent.select_move(obs)
        await self._fire(attacker, board, coord)
        if self._last_move:
            agent.receive_result(
                coord, self._last_move["result"], self._last_move["ship_sunk"]
            )

    async def _fire(self, attacker: str, board: GameBoard, coord: str) -> None:
        """Resolve a shot on board and record it as the last move. Invalid shots lose the turn."""
        try:
            row, col = parse_coordinate(coord)
            state, ship = board.receive_shot(row, col)
        except ValueError as e:
            log.warning("%s sent invalid shot '%s': %s", attacker, coord, e)
            return

        coord = format_coordinate(row, col)
        hit_name = ship.ship_type.name if (ship and state is CellState.HIT) else None
        sunk_name = ship.ship_type.name if (ship and ship.is_sunk) else None
        result_str = "HIT" if state is CellState.HIT else "MISS"
        msg = f"{attacker.capitalize()} fires {coord}: {result_str}"
        if hit_name:
            msg += f" — {hit_name}"
        if sunk_name:
            msg += " sunk!"
        if not self.headless:
            print(msg)
        log.debug(msg)

        if sunk_name:
            await self._send(
                {
                    "type": "ship_sunk",
                    "attacker": attacker,
                    "ship": sunk_name,
                    "turn": self._turn,
                }
            )

        self._last_move = {
            "player": attacker,
            "coordinate": coord,
            "result": result_str,
            "ship_hit": hit_name,
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

    def _obs(self, own: GameBoard, enemy: GameBoard) -> dict:
        return {
            "enemy_board": enemy.board_as_matrix(fog_of_war=True),
            "your_board": own.board_as_matrix(fog_of_war=False),
            "ships_sunk": {
                "by_you": enemy.ships_sunk_count(),
                "against_you": own.ships_sunk_count(),
            },
            "turn": self._turn,
        }

    def _agent_obs(self) -> dict:
        return self._obs(self.agent_board, self.player_board)

    def _player_view(self) -> dict:
        return {"type": "player_view", **self._obs(self.player_board, self.agent_board)}

    def _board_state(self, board: GameBoard, fog_of_war: bool) -> dict:
        return {
            "cells": board.board_as_matrix(fog_of_war=fog_of_war),
            "ships_remaining": len(board.board.ships) - board.ships_sunk_count(),
            "ships_sunk": board.ships_sunk_count(),
            "cells_hit": board.cells_hit_count(),
        }

    def _scores(self) -> dict:
        return {
            "player": {
                "ships_sunk": self.agent_board.ships_sunk_count(),
                "cells_hit": self.agent_board.cells_hit_count(),
            },
            "agent": {
                "ships_sunk": self.player_board.ships_sunk_count(),
                "cells_hit": self.player_board.cells_hit_count(),
            },
        }

    def _build_state_dict(self) -> dict:
        return {
            "type": "game_state",
            "game_id": self.ws_server.game_id if self.ws_server else None,
            "turn": self._turn,
            "current_player": self._current_player,
            "game_over": self._game_over,
            "winner": self._winner,
            "player_board": self._board_state(self.player_board, fog_of_war=False),
            "agent_board": self._board_state(self.agent_board, fog_of_war=True),
            "scores": self._scores(),
            "last_move": self._last_move,
        }

    def _build_game_over_dict(self) -> dict:
        return {
            "type": "game_over",
            "winner": self._winner,
            "total_turns": self._turn,
            "scores": self._scores(),
        }

    # ------------------------------------------------------------------
    # Scores
    # ------------------------------------------------------------------
    @property
    def player_score(self) -> dict:
        return {
            "sunk": self.agent_board.ships_sunk_count(),
            "hit": self.agent_board.cells_hit_count(),
        }

    @property
    def agent_score(self) -> dict:
        return {
            "sunk": self.player_board.ships_sunk_count(),
            "hit": self.player_board.cells_hit_count(),
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
        winner_label = "Player" if self._winner == "player" else "Agent"

        def _report_score(owner: str, score: dict) -> str:
            return f"  {owner:6s} — sunk: {score['sunk']}, hit: {score['hit']}"

        winner_turns = 0
        if self._winner == "player":
            winner_turns = self.agent_board.cells_targeted()
        else:
            winner_turns = self.player_board.cells_targeted()

        gameover_msg = f"GAME OVER — Winner: {winner_label} | Turns: {winner_turns:3d}"
        player_report = _report_score("Player", self.player_score)
        agent_report = _report_score("Agent", self.agent_score)

        log.info(gameover_msg)
        log.info(player_report)
        log.info(agent_report)
        log.info("-" * len(gameover_msg))
