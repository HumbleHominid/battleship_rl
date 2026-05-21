from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from game.coordinate_methods import format_coordinate
from game.game_board import GameBoard
from game.game_logger import GameLogger
from game.models import Board, CellState
from training.reward_fns import RewardFn, default_reward


class BattleshipEnv:
    """Fast single-game Battleship environment for RL training.

    Wraps GameBoard directly — no async, no WebSocket.

    Base reward structure (before any reward_fn shaping):
        - Every turn: -0.1
        - Hit:  +1.0
        - Ship sunk: +5.0
        - Win:  +10.0

    Args:
        reward_fn: Optional reward shaping function applied inside step().
                   Receives (action, pre_shot_cell_feats, base_reward, result,
                   ship_sunk, done) and returns the final reward. Defaults to
                   the identity (no shaping).

    Observation dict (compatible with GameEngine's agent_obs format):
        enemy_board:  10x10 list[list[str]] "SHIPTYPE:CELLSTATE" with fog of war
        your_board:   10x10 list[list[str]] all "NONE:EMPTY" (unused placeholder)
        ships_sunk:   {"by_you": int, "against_you": int}
        turn:         int
    """

    def __init__(
        self,
        reward_fn: RewardFn = default_reward,
        placement_method: Optional[str] = None,
    ) -> None:
        GameLogger.setup(console_level=logging.WARNING)
        self._board = GameBoard()
        self._turn = 0
        self._done = False
        self._reward_fn = reward_fn
        self._placement_method = placement_method

    # ------------------------------------------------------------------

    def reset(self) -> tuple[dict, dict]:
        import random
        from game.fleet_placement_methods import PLACEMENT_METHODS

        self._board = GameBoard()
        
        # Decide which placement method to use
        method = self._placement_method
        if method == "mix":
            # Exclude manual from mixed selection if it ever exists
            valid_methods = [m for m in PLACEMENT_METHODS.keys() if m != "manual"]
            method = random.choice(valid_methods)
            
        self._board.place_fleet(method=method)
        self._turn = 0
        self._done = False
        return self._get_obs(), {}

    def step(
        self,
        action: int,
        pre_shot_cell_feats: Optional[np.ndarray] = None,
    ) -> tuple[dict, float, bool, bool, dict]:
        """Take a shot at cell index `action` (row * 10 + col).

        Args:
            action: Cell index 0–99 (row * 10 + col).
            pre_shot_cell_feats: Optional (100, F) feature array encoding the
                board state before the shot. Required by reward fns that use
                Bayesian occupancy probabilities (e.g. bayes_augment_reward).

        Returns:
            obs, reward, terminated, truncated, info
        """
        if self._done:
            raise RuntimeError("Episode is over; call reset() first.")

        row, col = divmod(action, Board.board_size)
        coord = format_coordinate(row, col)
        cell_state, ship = self._board.receive_shot(row, col)

        self._turn += 1
        base_reward = -0.1

        sunk_name: str | None = None
        if cell_state is CellState.HIT:
            base_reward += 1.0
        if ship is not None and ship.is_sunk:
            sunk_name = ship.ship_type.name
            base_reward += 5.0

        self._done = self._board.all_ships_sunk()
        if self._done:
            base_reward += 10.0

        info = {
            "coordinate": coord,
            "result": cell_state.name,
            "ship_sunk": sunk_name,
        }
        reward = self._reward_fn(
            action,
            pre_shot_cell_feats,
            base_reward,
            cell_state.name,
            sunk_name,
            self._done,
        )
        return self._get_obs(), reward, self._done, False, info

    def legal_actions(self) -> list[int]:
        """Return list of cell indices (0–99) that have not yet been shot."""
        return [r * Board.board_size + c for r, c in self._board.get_unhit_cells()]

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
            "your_board": [
                ["NONE:EMPTY"] * Board.board_size for _ in range(Board.board_size)
            ],
            "ships_sunk": {
                "by_you": self._board.ships_sunk_count(),
                "against_you": 0,
            },
            "turn": self._turn,
        }
