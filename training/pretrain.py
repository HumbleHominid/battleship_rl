"""Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.

For each step the BayesianAgent selects the greedy argmax cell; the transformer
is trained to predict that cell via cross-entropy loss.

Usage:
    python training/pretrain.py --steps 200000 --checkpoint checkpoints/pretrain.pt
"""

from __future__ import annotations

import argparse
import os
import time

import torch
import torch.nn as nn
import torch.optim as optim

from game.agents.bayesian_agent import BayesianAgent
from game.agents.feature_extractor import FeatureExtractor
from game.agents.transformer_ppo_agent import TransformerPPONet
from game.coordinate_methods import parse_coordinate
from training.battleship_env import BattleshipEnv


def coord_to_index(coord: str) -> int:
    row, col = parse_coordinate(coord)
    return row * 10 + col


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=200_000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--log-interval", type=int, default=1_000)
    p.add_argument("--save-interval", type=int, default=10_000)
    p.add_argument("--checkpoint", type=str, default="checkpoints/pretrain.pt")
    p.add_argument("--device", type=str, default="cpu")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device(args.device)

    os.makedirs(os.path.dirname(args.checkpoint) or ".", exist_ok=True)

    net = TransformerPPONet().to(device)
    net.train()
    optimizer = optim.Adam(net.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    criterion = nn.NLLLoss()  # inputs are already log-probabilities from the network

    env = BattleshipEnv()
    extractor = FeatureExtractor()
    label_agent = BayesianAgent()

    obs, _ = env.reset()
    extractor.reset()
    label_agent.reset()

    total_loss = 0.0
    total_correct = 0
    episode_count = 0
    step = 0
    t0 = time.time()

    while step < args.steps:
        # Expert label
        expert_coord = label_agent.select_move(obs)
        target_idx = coord_to_index(expert_coord)

        # Features (uses extractor's internal bayes; select_move already called above
        # on a separate BayesianAgent instance, so no conflict)
        cell_np = extractor.compute_cell_features(obs)
        global_np = extractor.compute_global_features(
            obs["ships_sunk"]["by_you"], obs["turn"]
        )

        cell_t = torch.tensor(cell_np, dtype=torch.float32, device=device).unsqueeze(0)
        global_t = torch.tensor(
            global_np, dtype=torch.float32, device=device
        ).unsqueeze(0)
        legal_mask = cell_t[0, :, 12].bool().unsqueeze(0)
        target_t = torch.tensor([target_idx], dtype=torch.long, device=device)

        log_probs, _ = net(cell_t, global_t, legal_mask)
        loss = criterion(log_probs, target_t)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = log_probs[0].argmax().item()
        total_correct += int(pred == target_idx)
        step += 1

        # Advance environment following the expert policy
        action = coord_to_index(expert_coord)
        obs, _, done, _, info = env.step(action)
        extractor.update(info["coordinate"], info["result"], info["ship_sunk"])
        label_agent.receive_result(
            info["coordinate"], info["result"], info["ship_sunk"]
        )

        if done:
            episode_count += 1
            obs, _ = env.reset()
            extractor.reset()
            label_agent.reset()

        if step % args.log_interval == 0:
            avg_loss = total_loss / args.log_interval
            acc = total_correct / args.log_interval * 100
            elapsed = time.time() - t0
            print(
                f"step {step:7d} | loss {avg_loss:.4f} | acc {acc:.1f}% "
                f"| episodes {episode_count} | {elapsed:.1f}s"
            )
            total_loss = 0.0
            total_correct = 0
            t0 = time.time()

        if step % args.save_interval == 0:
            torch.save({"net_state": net.state_dict(), "step": step}, args.checkpoint)
            print(f"  saved checkpoint to {args.checkpoint}")

    torch.save({"net_state": net.state_dict(), "step": step}, args.checkpoint)
    print(f"Pretraining complete. Checkpoint: {args.checkpoint}")


if __name__ == "__main__":
    main()
