from __future__ import annotations

import torch
import torch.nn as nn

from game.agents.feature_extractor import CELL_FEATURE_DIM, GLOBAL_FEATURE_DIM
from game.agents.ppo_net._constants import D_MODEL, DIM_FF, DROPOUT, N_HEADS, N_LAYERS


class ValueNet(nn.Module):
    """Value trunk: cell + global features → scalar state value.

    A learned global token (projected from global features + a trainable embedding)
    is prepended to the cell token sequence; the value is read from position 0 of
    the encoder output.
    """

    def __init__(self) -> None:
        super().__init__()
        self.cell_proj = nn.Linear(CELL_FEATURE_DIM, D_MODEL)
        self.global_proj = nn.Linear(GLOBAL_FEATURE_DIM, D_MODEL)
        self.global_embed = nn.Parameter(torch.zeros(D_MODEL))
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
        self, cell_feats: torch.Tensor, global_feats: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            cell_feats:   (B, 100, CELL_FEATURE_DIM)
            global_feats: (B, GLOBAL_FEATURE_DIM)

        Returns:
            value: (B,)
        """
        value_tokens = self.cell_proj(cell_feats)
        global_token = self.global_proj(global_feats).unsqueeze(1) + self.global_embed
        seq = torch.cat([global_token, value_tokens], dim=1)
        out = self.encoder(seq)
        return self.head(out[:, 0, :]).squeeze(-1)
