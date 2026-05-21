from __future__ import annotations

import torch
import torch.nn as nn

_CELL_DIM = 4
_GLOBAL_DIM = 5
_N_ACTIONS = 100
_BOARD = 10


class QNetwork(nn.Module):
    """Dueling CNN Q-network for Battleship.

    Treats the 10x10 board as a spatial grid and extracts features with
    convolutions before predicting state-value and actions-advantage.

    Args:
        cell_feats:   (B, 100, 4)  per-cell features: [Bayesian prob, is_hit, is_miss, unshot_mask]
        global_feats: (B, 5)       binary sunk flag per ship (fleet order)
        legal_mask:   (B, 100)     True for cells that have not been shot

    Returns:
        q_values: (B, 100) with illegal cells masked to -1e9
    """

    def __init__(self) -> None:
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(_CELL_DIM, 32, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
        )
        
        # State-Value Stream V(s)
        self.value_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * _BOARD * _BOARD + _GLOBAL_DIM, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )
        
        # Advantage Stream A(s, a)
        self.advantage_head = nn.Sequential(
            nn.Conv2d(64 + _GLOBAL_DIM, 64, 1),
            nn.ReLU(),
            nn.Conv2d(64, 1, 1),
        )

    def forward(
        self,
        cell_feats: torch.Tensor,
        global_feats: torch.Tensor,
        legal_mask: torch.Tensor,
    ) -> torch.Tensor:
        B = cell_feats.shape[0]
        # Reshape to (B, _CELL_DIM, 10, 10)
        x = cell_feats.permute(0, 2, 1).reshape(B, _CELL_DIM, _BOARD, _BOARD)
        feats = self.backbone(x)  # (B, 64, 10, 10)
        
        # 1. Compute State-Value V(s)
        flat_feats = torch.cat([feats.reshape(B, -1), global_feats], dim=1) # (B, 6405)
        v = self.value_head(flat_feats)  # (B, 1)
        
        # 2. Compute Advantage A(s, a)
        g = global_feats.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, _BOARD, _BOARD)
        x_combined = torch.cat([feats, g], dim=1)  # (B, 69, 10, 10)
        adv = self.advantage_head(x_combined).reshape(B, _N_ACTIONS)  # (B, 100)
        
        # 3. Combine using Dueling formula
        q = v + (adv - adv.mean(dim=1, keepdim=True))  # (B, 100)
        
        return q.masked_fill(~legal_mask, -1e9)
