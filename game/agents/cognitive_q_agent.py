from __future__ import annotations

from typing import Optional

import torch

from game.agents.bayesian_agent import BayesianAgent
from game.agents.q_net import QNetwork
from game.agents.q_net.state_encoder import BayesEncoder, legal_mask_from_obs
from game.coordinate_methods import format_coordinate
from game.game_logger import GameLogger
from game.models import Board


class CognitiveQAgent(BayesianAgent):
    """Hierarchical Cognitive Q-Agent.

    Extends BayesianAgent to use standard Bayesian logical fallback when in
    target mode (i.e. when there are unresolved hit cells) and a custom
    DQN model (trained with human-prior reward shaping) when in search mode.
    """

    def __init__(
        self,
        checkpoint_path: Optional[str] = "checkpoints/q_cognitive.pt",
        device: str = "cpu",
        deterministic_selection: bool = False,
    ) -> None:
        super().__init__(deterministic_selection=deterministic_selection)
        self._device = torch.device(device)
        self.net = QNetwork().to(self._device)
        self.net.eval()
        self._encoder = BayesEncoder()

        if checkpoint_path is not None:
            ckpt = torch.load(checkpoint_path, map_location=self._device)
            self.net.load_state_dict(ckpt["net_state"])
            GameLogger.info(f"CognitiveQAgent loaded checkpoint {checkpoint_path}")

    def reset(self) -> None:
        super().reset()
        self._encoder.reset()

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        super().receive_result(coordinate, result, ship_sunk)
        self._encoder.update(coordinate, result, ship_sunk)

    def select_move(self, obs: dict) -> str:
        if not self._initialized:
            self._initialize_placements()
            self._recompute_grid()

        # Update unresolved hits state (copied/aligned with BayesianAgent logic)
        board = obs["enemy_board"]
        sunk_names = {st.name for st in self._sunk_ship_types}
        unshot_cells: list[tuple[int, int]] = []
        hits_changed = False

        for r in range(Board.board_size):
            for c in range(Board.board_size):
                ship_name, state = board[r][c].split(":")
                if state == "EMPTY":
                    unshot_cells.append((r, c))
                elif state == "HIT" and ship_name in sunk_names:
                    if (r, c) in self._unresolved_hits:
                        self._unresolved_hits.discard((r, c))
                        hits_changed = True

        if hits_changed:
            self._recompute_grid()

        if not unshot_cells:
            raise RuntimeError("No unshot cells remain")

        # Hierarchical switch: Target Mode -> Use BayesianAgent target hunt
        if len(self._unresolved_hits) > 0:
            GameLogger.debug("Cognitive-Q in Target Mode: falling back to Bayesian agent")
            return super().select_move(obs)

        # Search Mode -> Use the Q-network model
        cell_np, global_np = self._encoder.encode(obs)

        cell_t = torch.tensor(
            cell_np, dtype=torch.float32, device=self._device
        ).unsqueeze(0)
        global_t = torch.tensor(
            global_np, dtype=torch.float32, device=self._device
        ).unsqueeze(0)
        legal = legal_mask_from_obs(obs)
        legal_t = torch.tensor(legal, dtype=torch.bool, device=self._device).unsqueeze(
            0
        )

        with torch.no_grad():
            q_values = self.net(cell_t, global_t, legal_t)

        action = int(q_values[0].argmax().item())
        row, col = divmod(action, Board.board_size)
        coord = format_coordinate(row, col)
        GameLogger.debug(
            "Cognitive-Q shooting search move %s (q=%.3f)", coord, float(q_values[0, action].item())
        )
        return coord

    def save(self, path: str) -> None:
        torch.save({"net_state": self.net.state_dict()}, path)
