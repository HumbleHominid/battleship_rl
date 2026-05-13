from __future__ import annotations

from typing import Optional

import numpy as np

from game.agents.bayesian_agent import BayesianAgent
from game.models import Board, Ship


def legal_mask_from_obs(obs: dict) -> np.ndarray:
    """Return (100,) bool array — True for cells that have not yet been shot."""
    board = obs["enemy_board"]
    size = Board.board_size
    mask = np.zeros(size * size, dtype=bool)
    for r in range(size):
        for c in range(size):
            _, cell_state = board[r][c].split(":")
            if cell_state == "EMPTY":
                mask[r * size + c] = True
    return mask


class BayesEncoder:
    """Stateful encoder that wraps BayesianAgent to produce Q-network features.

    Must be reset at the start of each episode and updated after each shot.

    Usage:
        encoder.reset()
        cell_feats, global_feats = encoder.encode(obs)   # before action
        encoder.update(coord, result, ship_sunk)          # after action result
    """

    def __init__(self) -> None:
        self._bayes = BayesianAgent()
        self._sunk_ships: set[str] = set()

    def reset(self) -> None:
        self._bayes.reset()
        self._sunk_ships = set()

    def update(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        self._bayes.receive_result(coordinate, result, ship_sunk)
        if ship_sunk is not None:
            self._sunk_ships.add(ship_sunk)

    def encode(self, obs: dict) -> tuple[np.ndarray, np.ndarray]:
        """Encode game observation into feature tensors.

        Returns:
            cell_feats:   (100, 3) float32 — [Bayesian prob, is_hit, is_miss] per cell
            global_feats: (5,)    float32 — binary sunk flag per ship
        """
        self._bayes.resolve_sunk_hits(obs)

        # Channel 0: normalized Bayesian occupancy probability
        total_grid = np.array(self._bayes._grid, dtype=np.float32).reshape(Board.board_size ** 2)
        total_max = total_grid.max()
        if total_max > 0:
            total_grid /= total_max

        # Channels 1 & 2: binary hit / miss from observation
        board = obs["enemy_board"]
        hit = np.zeros(Board.board_size ** 2, dtype=np.float32)
        miss = np.zeros(Board.board_size ** 2, dtype=np.float32)
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                _, state = board[r][c].split(":")
                idx = r * Board.board_size + c
                if state == "HIT":
                    hit[idx] = 1.0
                elif state == "MISS":
                    miss[idx] = 1.0

        cell_feats = np.stack([total_grid, hit, miss], axis=1)  # (100, 3)

        fleet = Ship.get_fleet()
        global_feats = np.array(
            [1.0 if ship_type.name in self._sunk_ships else 0.0 for ship_type in fleet],
            dtype=np.float32,
        )

        return cell_feats, global_feats
