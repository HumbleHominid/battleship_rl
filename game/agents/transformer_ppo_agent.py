from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from game.agents.base_agent import BaseAgent
from game.agents.feature_extractor import (
    CELL_FEATURE_DIM,
    GLOBAL_FEATURE_DIM,
    FeatureExtractor,
)
from game.coordinate_methods import format_coordinate
from game.models import Board

_D_MODEL = 128
_N_HEADS = 4
_N_LAYERS = 4
_DIM_FF = 512
_DROPOUT = 0.1


class TransformerPPONet(nn.Module):
    """Transformer actor-critic network for Battleship with separate policy and value trunks.

    Policy trunk: cell_proj → 4-layer encoder → policy_head (per-cell logit).
    Value trunk:  value_cell_proj + global_proj → 4-layer encoder → value_head (global token).
    Trunks share no parameters so value gradients cannot corrupt pretrained policy weights.
    """

    def __init__(self) -> None:
        super().__init__()

        # Policy trunk
        self.policy_cell_proj = nn.Linear(CELL_FEATURE_DIM, _D_MODEL)
        policy_layer = nn.TransformerEncoderLayer(
            d_model=_D_MODEL,
            nhead=_N_HEADS,
            dim_feedforward=_DIM_FF,
            dropout=_DROPOUT,
            activation="gelu",
            batch_first=True,
        )
        self.policy_encoder = nn.TransformerEncoder(policy_layer, num_layers=_N_LAYERS)
        self.policy_head = nn.Sequential(
            nn.Linear(_D_MODEL, 64),
            nn.GELU(),
            nn.Linear(64, 1),
        )

        # Value trunk
        self.value_cell_proj = nn.Linear(CELL_FEATURE_DIM, _D_MODEL)
        self.global_proj = nn.Linear(GLOBAL_FEATURE_DIM, _D_MODEL)
        self.global_embed = nn.Parameter(torch.zeros(_D_MODEL))
        value_layer = nn.TransformerEncoderLayer(
            d_model=_D_MODEL,
            nhead=_N_HEADS,
            dim_feedforward=_DIM_FF,
            dropout=_DROPOUT,
            activation="gelu",
            batch_first=True,
        )
        self.value_encoder = nn.TransformerEncoder(value_layer, num_layers=_N_LAYERS)
        self.value_head = nn.Sequential(
            nn.Linear(_D_MODEL, 64),
            nn.GELU(),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        cell_feats: torch.Tensor,
        global_feats: torch.Tensor,
        legal_mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            cell_feats:  (B, 100, CELL_FEATURE_DIM)
            global_feats: (B, GLOBAL_FEATURE_DIM)
            legal_mask:  (B, 100) bool, True = legal action

        Returns:
            log_probs: (B, 100) — log softmax over cells (illegal = -inf before softmax)
            value:     (B,)
        """
        # Policy path: cell tokens only
        policy_tokens = self.policy_cell_proj(cell_feats)  # (B, 100, D)
        policy_out = self.policy_encoder(policy_tokens)  # (B, 100, D)
        logits = self.policy_head(policy_out).squeeze(-1)  # (B, 100)
        logits = logits.masked_fill(~legal_mask, float("-inf"))
        log_probs = F.log_softmax(logits, dim=-1)

        # Value path: global token + all cell tokens
        value_tokens = self.value_cell_proj(cell_feats)  # (B, 100, D)
        global_token = (
            self.global_proj(global_feats).unsqueeze(1) + self.global_embed
        )  # (B, 1, D)
        value_seq = torch.cat([global_token, value_tokens], dim=1)  # (B, 101, D)
        value_out = self.value_encoder(value_seq)  # (B, 101, D)
        value = self.value_head(value_out[:, 0, :]).squeeze(-1)  # (B,)

        return log_probs, value


class TransformerPPOAgent(BaseAgent):
    """Battleship agent backed by a Transformer actor-critic network.

    Operates in deterministic (argmax) mode during game play. For training,
    use the net directly via the training scripts.

    Args:
        checkpoint_path: Optional path to a saved checkpoint (.pt file).
        device: torch device string; defaults to "cpu".
    """

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        self._device = torch.device(device)
        self.net = TransformerPPONet().to(self._device)
        self.net.eval()
        self._extractor = FeatureExtractor()

        if checkpoint_path is not None:
            self.load(checkpoint_path)

    def reset(self) -> None:
        self._extractor.reset()

    def select_move(self, obs: dict) -> str:
        ships_sunk = obs["ships_sunk"]["by_you"]
        turn = obs["turn"]

        cell_np = self._extractor.compute_cell_features(obs)
        global_np = self._extractor.compute_global_features(ships_sunk, turn)

        cell_t = torch.tensor(
            cell_np, dtype=torch.float32, device=self._device
        ).unsqueeze(0)
        global_t = torch.tensor(
            global_np, dtype=torch.float32, device=self._device
        ).unsqueeze(0)
        legal_mask = cell_t[0, :, 12].bool().unsqueeze(0)  # (1, 100)

        with torch.no_grad():
            log_probs, _ = self.net(cell_t, global_t, legal_mask)

        action = log_probs[0].argmax().item()
        row, col = divmod(action, Board.board_size)
        return format_coordinate(row, col)

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        self._extractor.update(coordinate, result, ship_sunk)

    def save(self, path: str) -> None:
        torch.save({"net_state": self.net.state_dict()}, path)

    @classmethod
    def load(cls, path: str, device: str = "cpu") -> "TransformerPPOAgent":
        agent = cls(device=device)
        ckpt = torch.load(path, map_location=device)
        agent.net.load_state_dict(ckpt["net_state"])
        return agent
