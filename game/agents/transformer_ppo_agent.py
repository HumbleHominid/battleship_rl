from __future__ import annotations

from typing import Optional

import torch

from game.agents.base_agent import BaseAgent
from game.agents.feature_extractor import FeatureExtractor
from game.agents.ppo_net import TransformerPPONet
from game.coordinate_methods import format_coordinate
from game.models import Board


class TransformerPPOAgent(BaseAgent):
    """Battleship agent backed by a Transformer actor-critic network.

    Operates in deterministic (argmax) mode during game play. For training,
    use TransformerPPONet directly via the training scripts.

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
