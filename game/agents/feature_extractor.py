from __future__ import annotations

import numpy as np

from game.agents.bayesian_agent import BayesianAgent
from game.coordinate_methods import parse_coordinate
from game.models import Board, Ship, get_ship_size

_MAX_L1_DIST = 2 * (Board.board_size - 1)
_N_SHIP_TYPES = len(Ship.get_fleet())
CELL_FEATURE_DIM = 16
GLOBAL_FEATURE_DIM = 4
_MAX_TOTAL_HITS = sum(get_ship_size(ship_type) for ship_type in Ship.get_fleet())


class FeatureExtractor:
    """Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agent.

    Internally wraps a BayesianAgent to compute occupancy probabilities, and
    maintains a separate board-state array for structural features.

    Usage:
        extractor.reset()                        # start of episode
        feats = extractor.compute_cell_features(obs)   # before each action
        glob = extractor.compute_global_features(ships_sunk, turn)
        extractor.update(coord, result, ship_sunk)     # after each action result
    """

    def __init__(self) -> None:
        self._bayes = BayesianAgent()
        # 0 = unknown/EMPTY, 1 = HIT, 2 = MISS
        self._board_state = np.zeros(
            (Board.board_size, Board.board_size), dtype=np.int8
        )

    def reset(self) -> None:
        self._bayes.reset()
        self._board_state[:] = 0

    def update(self, coordinate: str, result: str, ship_sunk: str | None) -> None:
        """Record the outcome of a shot and propagate to the internal Bayesian model."""
        row, col = parse_coordinate(coordinate)
        self._board_state[row, col] = 1 if result == "HIT" else 2
        self._bayes.receive_result(coordinate, result, ship_sunk)

    def compute_cell_features(self, obs: dict) -> np.ndarray:
        """Return shape (100, 16) float32 feature array for all cells.

        Calls BayesianAgent.select_move(obs) internally to refresh the occupancy
        grid and clean up resolved hits; the returned move is discarded.
        """
        # Refresh grid; also discards resolved hits for sunk ships
        self._bayes.select_move(obs)

        total_grid = np.array(self._bayes._grid, dtype=np.float32)
        total_max = total_grid.max()
        total_norm = total_grid / total_max if total_max > 0 else total_grid

        # Per-ship-type occupancy grids (same target-mode logic as BayesianAgent)
        per_type = np.zeros(
            (_N_SHIP_TYPES, Board.board_size, Board.board_size), dtype=np.float32
        )
        target_mode = len(self._bayes._unresolved_hits) > 0
        for i, ship_type in enumerate(Ship.get_fleet()):
            if ship_type not in self._bayes._valid_placements:
                continue
            for placement in self._bayes._valid_placements[ship_type]:
                if target_mode and not (placement & self._bayes._unresolved_hits):
                    continue
                for r, c in placement:
                    per_type[i, r, c] += 1.0
            type_max = per_type[i].max()
            if type_max > 0:
                per_type[i] /= type_max

        hit_positions = (
            list(zip(*np.where(self._board_state == 1)))
            if np.any(self._board_state == 1)
            else []
        )

        features = np.zeros(
            (Board.board_size, Board.board_size, CELL_FEATURE_DIM), dtype=np.float32
        )
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                f = features[r, c]
                state = int(self._board_state[r, c])

                f[0] = total_norm[r, c]
                f[1:6] = per_type[:, r, c]
                f[6 + state] = 1.0  # one-hot known state (6=unknown, 7=hit, 8=miss)

                if hit_positions:
                    f[9] = (
                        min(abs(r - hr) + abs(c - hc) for hr, hc in hit_positions)
                        / _MAX_L1_DIST
                    )
                else:
                    f[9] = 1.0

                adj_hit = adj_unknown = 0
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < Board.board_size and 0 <= nc < Board.board_size:
                        ns = int(self._board_state[nr, nc])
                        if ns == 1:
                            adj_hit += 1
                        elif ns == 0:
                            adj_unknown += 1
                f[10] = adj_hit / 4.0
                f[11] = adj_unknown / 4.0
                f[12] = 1.0 if state == 0 else 0.0
                f[13] = r / (Board.board_size - 1)
                f[14] = c / (Board.board_size - 1)
                f[15] = float((r + c) % 2)

        return features.reshape(Board.board_size**2, CELL_FEATURE_DIM)

    def compute_global_features(self, ships_sunk: int, turn: int) -> np.ndarray:
        """Return shape (4,) float32 global context vector."""
        total_hits = int(np.sum(self._board_state == 1))
        return np.array(
            [
                ships_sunk / 5.0,
                (5 - ships_sunk) / 5.0,
                min(turn / (Board.board_size**2), 1.0),
                total_hits / _MAX_TOTAL_HITS,
            ],
            dtype=np.float32,
        )
