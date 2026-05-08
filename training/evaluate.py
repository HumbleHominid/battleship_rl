from __future__ import annotations

import numpy as np
import torch

from game.agents.bayesian_agent import BayesianAgent
from game.agents.feature_extractor import FeatureExtractor
from game.agents.ppo_net import TransformerPPONet
from game.coordinate_methods import parse_coordinate
from game.models import Board
from training.battleship_env import BattleshipEnv


def evaluate(
    net: TransformerPPONet,
    n_games: int,
    device: torch.device,
) -> float:
    """Return mean turns-to-win over n_games episodes (greedy policy)."""
    net.eval()
    env = BattleshipEnv()
    extractor = FeatureExtractor()
    turns_list = []

    for _ in range(n_games):
        obs, _ = env.reset()
        extractor.reset()
        while not env.done:
            cell_np = extractor.compute_cell_features(obs)
            global_np = extractor.compute_global_features(
                obs["ships_sunk"]["by_you"], obs["turn"]
            )
            cell_t = torch.tensor(
                cell_np, dtype=torch.float32, device=device
            ).unsqueeze(0)
            global_t = torch.tensor(
                global_np, dtype=torch.float32, device=device
            ).unsqueeze(0)
            legal_mask = cell_t[0, :, 12].bool().unsqueeze(0)
            with torch.no_grad():
                log_probs, _ = net(cell_t, global_t, legal_mask)
            action = log_probs[0].argmax().item()
            obs, _, _, _, info = env.step(action)
            extractor.update(info["coordinate"], info["result"], info["ship_sunk"])
        turns_list.append(env.turn)

    net.train()
    return float(np.mean(turns_list))


def bayes_baseline(n_games: int = 100) -> float:
    """Return mean turns-to-win for BayesianAgent (one-time reference)."""
    env = BattleshipEnv()
    agent = BayesianAgent()
    turns_list = []
    for _ in range(n_games):
        obs, _ = env.reset()
        agent.reset()
        while not env.done:
            coord = agent.select_move(obs)
            row, col = parse_coordinate(coord)
            action = row * Board.board_size + col
            obs, _, _, _, info = env.step(action)
            agent.receive_result(info["coordinate"], info["result"], info["ship_sunk"])
        turns_list.append(env.turn)
    return float(np.mean(turns_list))
