from __future__ import annotations

import numpy as np

from game.models import Board

# Cell state indices in the one-hot encoding
_UNKNOWN = 0
_HIT = 1
_MISS = 2


def encode_obs(obs: dict) -> tuple[np.ndarray, np.ndarray]:
    """Encode a game observation into flat tensors for the Q-network.

    Returns:
        cell_feats:   (100, 3) float32 — one-hot {unknown, hit, miss} per cell
        global_feats: (2,)    float32 — [ships_sunk / 5.0, min(turn / 100, 1.0)]
    """
    board = obs["enemy_board"]
    size = Board.board_size
    cell_feats = np.zeros((size * size, 3), dtype=np.float32)

    for r in range(size):
        for c in range(size):
            cell_str = board[r][c]
            _, cell_state = cell_str.split(":")
            idx = r * size + c
            if cell_state == "HIT":
                cell_feats[idx, _HIT] = 1.0
            elif cell_state == "MISS":
                cell_feats[idx, _MISS] = 1.0
            else:
                cell_feats[idx, _UNKNOWN] = 1.0

    ships_sunk = obs["ships_sunk"]["by_you"]
    turn = obs["turn"]
    global_feats = np.array(
        [ships_sunk / 5.0, min(turn / 100.0, 1.0)], dtype=np.float32
    )

    return cell_feats, global_feats
