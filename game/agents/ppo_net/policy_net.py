from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from game.agents.feature_extractor import CELL_FEATURE_DIM
from game.agents.ppo_net._constants import D_MODEL, DIM_FF, DROPOUT, N_HEADS, N_LAYERS


class PolicyNet(nn.Module):
    """Policy trunk: cell features → transformer encoder → per-cell log-probabilities."""

    def __init__(self) -> None:
        super().__init__()
        self.cell_proj = nn.Linear(CELL_FEATURE_DIM, D_MODEL)
        layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL,
            nhead=N_HEADS,
            dim_feedforward=DIM_FF,
            dropout=DROPOUT,
            activation="gelu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=N_LAYERS)
        self.head = nn.Sequential(
            nn.Linear(D_MODEL, 64),
            nn.GELU(),
            nn.Linear(64, 1),
        )

    def forward(
        self, cell_feats: torch.Tensor, legal_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            cell_feats:  (B, 100, CELL_FEATURE_DIM)
            legal_mask:  (B, 100) bool — True = legal action

        Returns:
            log_probs: (B, 100) — illegal cells masked to -inf before softmax
        """
        tokens = self.cell_proj(cell_feats)
        out = self.encoder(tokens)
        logits = self.head(out).squeeze(-1)
        logits = logits.masked_fill(~legal_mask, float("-inf"))
        return F.log_softmax(logits, dim=-1)
