from __future__ import annotations

import torch
import torch.nn as nn

_CELL_DIM = 1
_GLOBAL_DIM = 5
_N_ACTIONS = 100


class QNetwork(nn.Module):
    """MLP Q-network for Battleship.

    Maps a board state to a Q-value for each of the 100 cells.

    Args:
        cell_feats:   (B, 100, 1)  Bayesian total-occupancy probability per cell
        global_feats: (B, 5)       binary sunk flag per ship (fleet order)
        legal_mask:   (B, 100)     True for cells that have not been shot

    Returns:
        q_values: (B, 100) with illegal cells masked to -1e9
    """

    def __init__(self) -> None:
        super().__init__()
        in_dim = _CELL_DIM * _N_ACTIONS + _GLOBAL_DIM
        self.net = nn.Sequential(
            nn.Linear(in_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, _N_ACTIONS),
        )

    def forward(
        self,
        cell_feats: torch.Tensor,
        global_feats: torch.Tensor,
        legal_mask: torch.Tensor,
    ) -> torch.Tensor:
        flat = cell_feats.flatten(start_dim=1)  # (B, 100)
        x = torch.cat([flat, global_feats], dim=1)  # (B, 105)
        q = self.net(x)  # (B, 100)
        q = q.masked_fill(~legal_mask, -1e9)
        return q
