from __future__ import annotations

from typing import Optional

import torch

from game.agents.base_agent import BaseAgent
from game.agents.q_net import QNetwork
from game.agents.q_net.state_encoder import encode_obs
from game.coordinate_methods import format_coordinate
from game.models import Board


class QAgent(BaseAgent):
    """Battleship agent backed by a Q-network (DQN).

    Operates in greedy mode (epsilon=0) during game play. For training,
    use QNetwork directly via training/q_learning/q_train.py.

    Args:
        checkpoint_path: Optional path to a saved .pt checkpoint.
        device: torch device string; defaults to "cpu".
    """

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        self._device = torch.device(device)
        self.net = QNetwork().to(self._device)
        self.net.eval()

        if checkpoint_path is not None:
            ckpt = torch.load(checkpoint_path, map_location=self._device)
            self.net.load_state_dict(ckpt["net_state"])

    def reset(self) -> None:
        pass

    def select_move(self, obs: dict) -> str:
        cell_np, global_np = encode_obs(obs)

        cell_t = torch.tensor(cell_np, dtype=torch.float32, device=self._device).unsqueeze(0)
        global_t = torch.tensor(global_np, dtype=torch.float32, device=self._device).unsqueeze(0)

        # Legal mask: cells that are still unknown (not yet shot)
        legal_mask = (cell_t[0, :, 0] == 1.0).unsqueeze(0)  # (1, 100)

        with torch.no_grad():
            q_values = self.net(cell_t, global_t, legal_mask)

        action = q_values[0].argmax().item()
        row, col = divmod(action, Board.board_size)
        return format_coordinate(row, col)

    def save(self, path: str) -> None:
        torch.save({"net_state": self.net.state_dict()}, path)
