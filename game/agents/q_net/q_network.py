from __future__ import annotations

import torch
import torch.nn as nn

_CELL_DIM = 3
_GLOBAL_DIM = 5
_N_ACTIONS = 100
_BOARD = 10


class QNetwork(nn.Module):
    """CNN Q-network for Battleship.

    Treats the 10×10 board as a spatial grid and extracts features with
    convolutions before predicting a Q-value per cell.

    Args:
        cell_feats:   (B, 100, 3)  per-cell features: [Bayesian prob, is_hit, is_miss]
        global_feats: (B, 5)       binary sunk flag per ship (fleet order)
        legal_mask:   (B, 100)     True for cells that have not been shot

    Returns:
        q_values: (B, 100) with illegal cells masked to -1e9
    """

    def __init__(self) -> None:
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(_CELL_DIM, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1),         nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),         nn.ReLU(),
        )
        self.head = nn.Sequential(
            nn.Conv2d(64 + _GLOBAL_DIM, 64, 1), nn.ReLU(),
            nn.Conv2d(64, 1, 1),
        )

    def forward(
        self,
        cell_feats: torch.Tensor,
        global_feats: torch.Tensor,
        legal_mask: torch.Tensor,
    ) -> torch.Tensor:
        B = cell_feats.shape[0]
        x = cell_feats.permute(0, 2, 1).reshape(B, _CELL_DIM, _BOARD, _BOARD)
        x = self.backbone(x)                                                      # (B, 64, 10, 10)
        g = global_feats.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, _BOARD, _BOARD)
        x = torch.cat([x, g], dim=1)                                              # (B, 69, 10, 10)
        q = self.head(x).reshape(B, _N_ACTIONS)                                   # (B, 100)
        return q.masked_fill(~legal_mask, -1e9)
