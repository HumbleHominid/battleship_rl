from __future__ import annotations

import torch.nn as nn

from game.agents.ppo_net.policy_net import PolicyNet
from game.agents.ppo_net.value_net import ValueNet

__all__ = ["TransformerPPONet", "PolicyNet", "ValueNet"]


class TransformerPPONet(nn.Module):
    """Transformer actor-critic with fully separate policy and value trunks.

    Policy trunk: cell features → PolicyNet → masked log-softmax over cells.
    Value trunk:  cell + global features → ValueNet → scalar.

    Trunks share no parameters — value gradients cannot corrupt pretrained policy weights.
    Arch hyperparameters are in _constants.py.
    """

    def __init__(self) -> None:
        super().__init__()
        self.policy = PolicyNet()
        self.value = ValueNet()

    def forward(
        self,
        cell_feats,
        global_feats,
        legal_mask,
    ):
        """
        Args:
            cell_feats:   (B, 100, CELL_FEATURE_DIM)
            global_feats: (B, GLOBAL_FEATURE_DIM)
            legal_mask:   (B, 100) bool

        Returns:
            log_probs: (B, 100)
            value:     (B,)
        """
        return self.policy(cell_feats, legal_mask), self.value(cell_feats, global_feats)

    def policy_params(self) -> list:
        return list(self.policy.parameters())

    def value_params(self) -> list:
        return list(self.value.parameters())
