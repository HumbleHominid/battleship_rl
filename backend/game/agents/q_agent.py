from __future__ import annotations

import logging
from typing import Optional

import torch

from game.agents.base_agent import BaseAgent
from game.agents.q_net import QNetwork
from game.agents.q_net.state_encoder import BayesEncoder, legal_mask_from_obs
from game.coordinate_methods import format_coordinate
from game.models import Board

log = logging.getLogger(__name__)


class QAgent(BaseAgent):
    """Battleship agent backed by a Q-network (DQN).

    Operates in greedy mode (epsilon=0) during game play. For training,
    use QNetwork directly via training/q_train.py.

    Args:
        checkpoint_path: Path to a saved .pt checkpoint.
    """

    def __init__(self, checkpoint_path: str = "checkpoints/q_agent.pt") -> None:
        self.net = QNetwork()
        self.net.eval()
        self._encoder = BayesEncoder()

        ckpt = torch.load(checkpoint_path, map_location="cpu")
        self.net.load_state_dict(ckpt["net_state"])

    def reset(self) -> None:
        self._encoder.reset()

    def select_move(self, obs: dict) -> str:
        cell_np, global_np = self._encoder.encode(obs)

        cell_t = torch.tensor(cell_np, dtype=torch.float32).unsqueeze(0)
        global_t = torch.tensor(global_np, dtype=torch.float32).unsqueeze(0)
        legal = legal_mask_from_obs(obs)
        legal_t = torch.tensor(legal, dtype=torch.bool).unsqueeze(0)

        with torch.no_grad():
            q_values = self.net(cell_t, global_t, legal_t)

        action = int(q_values[0].argmax().item())
        row, col = divmod(action, Board.board_size)
        coord = format_coordinate(row, col)
        log.debug(
            "Q-agent shooting %s (q=%.3f)", coord, float(q_values[0, action].item())
        )
        return coord

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        self._encoder.update(coordinate, result, ship_sunk)
