from __future__ import annotations

from game.coordinate_methods import format_coordinate
from game.game_board import GameBoard
from game.models import CellState


class BattleshipEnv:
    """Fast single-game Battleship environment for RL training.

    Wraps GameBoard directly — no async, no WebSocket.

    Reward structure:
        - Every turn: -0.1
        - Miss: -0.1 (in addition to turn penalty → -0.2 total)
        - Win:  +10.0

    Observation dict (compatible with GameEngine's agent_obs format):
        enemy_board:  10x10 list[list[str]] "SHIPTYPE:CELLSTATE" with fog of war
        your_board:   10x10 list[list[str]] all "NONE:EMPTY" (unused placeholder)
        ships_sunk:   {"by_you": int, "against_you": int}
        turn:         int
    """

    def __init__(self) -> None:
        self._board = GameBoard()
        self._turn = 0
        self._done = False

    # ------------------------------------------------------------------

    def reset(self) -> tuple[dict, dict]:
        self._board = GameBoard()
        self._board.place_fleet()
        self._turn = 0
        self._done = False
        return self._get_obs(), {}

    def step(self, action: int) -> tuple[dict, float, bool, bool, dict]:
        """Take a shot at cell index `action` (row * 10 + col).

        Returns:
            obs, reward, terminated, truncated, info
        """
        if self._done:
            raise RuntimeError("Episode is over; call reset() first.")

        row, col = divmod(action, 10)
        coord = format_coordinate(row, col)
        cell_state, ship = self._board.receive_shot(row, col)

        self._turn += 1
        reward = -0.1  # per-turn penalty

        sunk_name: str | None = None
        if cell_state is CellState.MISS:
            reward -= 0.1
        elif ship is not None and ship.is_sunk:
            sunk_name = ship.ship_type.name

        self._done = self._board.all_ships_sunk()
        if self._done:
            reward += 10.0

        info = {
            "coordinate": coord,
            "result": cell_state.name,
            "ship_sunk": sunk_name,
        }
        return self._get_obs(), reward, self._done, False, info

    def legal_actions(self) -> list[int]:
        """Return list of cell indices (0–99) that have not yet been shot."""
        return [r * 10 + c for r, c in self._board.get_unhit_cells()]

    @property
    def done(self) -> bool:
        return self._done

    @property
    def turn(self) -> int:
        return self._turn

    # ------------------------------------------------------------------

    def _get_obs(self) -> dict:
        return {
            "enemy_board": self._board.board_as_matrix(fog_of_war=True),
            "your_board": [["NONE:EMPTY"] * 10 for _ in range(10)],
            "ships_sunk": {
                "by_you": self._board.ships_sunk_count(),
                "against_you": 0,
            },
            "turn": self._turn,
        }
