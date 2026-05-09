"""Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.

For each step the BayesianAgent selects the greedy argmax cell; the transformer
is trained to predict that cell via cross-entropy loss.

Usage:
    python training/pretrain.py --steps 200000 --checkpoint checkpoints/pretrain.pt
"""

from __future__ import annotations

import argparse
import logging
import os
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR

from game.agents.bayesian_agent import BayesianAgent
from game.agents.feature_extractor import FeatureExtractor
from game.agents.ppo_net import TransformerPPONet
from game.coordinate_methods import parse_coordinate
from game.models import Board, Ship, ShipType
from training.battleship_env import BattleshipEnv
from training.training_logger import TrainingLogger


def coord_to_index(coord: str) -> int:
    row, col = parse_coordinate(coord)
    return row * Board.board_size + col


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=200_000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--log-interval", type=int, default=1_000)
    p.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    p.add_argument("--save-interval", type=int, default=10_000)
    p.add_argument("--checkpoint", type=str, default="checkpoints/pretrain.pt")
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument("--warmup-steps", type=int, default=2_000)
    p.add_argument("--board-size", type=int, default=10)
    p.add_argument(
        "--fleet-config",
        nargs="+",
        default=[
            ShipType.CARRIER.name,
            ShipType.BATTLESHIP.name,
            ShipType.DESTROYER.name,
            ShipType.SUBMARINE.name,
            ShipType.PATROL_BOAT.name,
        ],
    )
    return p.parse_args()


def setup_board_and_fleet(args: argparse.Namespace) -> None:
    Board.board_size = args.board_size
    valid_ships = set(ship.name for ship in ShipType if ship != ShipType.NONE)
    selected_ships = []
    for ship_name in args.fleet_config:
        if ship_name not in valid_ships:
            msg = f"Invalid ship '{ship_name}' in fleet config. Valid options: {valid_ships}"
            TrainingLogger.error(msg)
            raise ValueError(msg)
        selected_ships.append(ShipType[ship_name])
    Ship.valid_ships = selected_ships
    TrainingLogger.debug(
        f"Selected ships for fleet: {[ship.name for ship in Ship.valid_ships]}"
    )


def init_transformer_ppo(
    args: argparse.Namespace, device: torch.device
) -> tuple[
    TransformerPPONet, list[nn.Parameter], optim.Optimizer, SequentialLR, nn.NLLLoss
]:
    net = TransformerPPONet().to(device)
    net.train()
    policy_params = net.policy_params()
    optimizer = optim.Adam(policy_params, lr=args.lr, weight_decay=args.weight_decay)
    scheduler = SequentialLR(
        optimizer,
        schedulers=[
            LinearLR(
                optimizer,
                start_factor=0.01,
                end_factor=1.0,
                total_iters=args.warmup_steps,
            ),
            CosineAnnealingLR(
                optimizer, T_max=max(1, args.steps - args.warmup_steps), eta_min=1e-5
            ),
        ],
        milestones=[args.warmup_steps],
    )
    criterion = nn.NLLLoss()  # inputs are already log-probabilities from the network
    return net, policy_params, optimizer, scheduler, criterion


def run_training_loop(
    args: argparse.Namespace,
    device: torch.device,
) -> None:
    # Transformer setup
    net, policy_params, optimizer, scheduler, criterion = init_transformer_ppo(
        args, device
    )

    # Environment setup
    env = BattleshipEnv()
    extractor = FeatureExtractor()
    label_agent = BayesianAgent(deterministic_selection=True)

    def env_reset() -> tuple[dict, dict]:
        extractor.reset()
        label_agent.reset()
        return env.reset()

    def interval_reset() -> tuple[float, int, int, float]:
        return 0.0, 0, 0, time.time()

    episode_count = 0
    step = 0
    obs, _ = env_reset()
    total_loss, total_correct, log_steps, t0 = interval_reset()

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

        # gradient step
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(policy_params, 1.0)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        pred = log_probs[0].argmax().item()
        total_correct += int(pred == target_idx)
        step += 1
        log_steps += 1

        # Advance environment following the expert policy
        action = coord_to_index(expert_coord)
        obs, _, done, _, info = env.step(action)
        extractor.update(info["coordinate"], info["result"], info["ship_sunk"])
        label_agent.receive_result(
            info["coordinate"], info["result"], info["ship_sunk"]
        )

        if done:
            episode_count += 1
            obs, _ = env_reset()

        if step == 1 or step % args.log_interval == 0:
            avg_loss = total_loss / log_steps
            acc = total_correct / log_steps * 100
            elapsed = time.time() - t0
            TrainingLogger.info(
                f"step {step:7d} | loss {avg_loss:.4f} | acc {acc:.1f}% "
                f"| episodes {episode_count} | {elapsed:.1f}s"
            )
            total_loss, total_correct, log_steps, t0 = interval_reset()

        if step % args.save_interval == 0:
            torch.save({"net_state": net.state_dict(), "step": step}, args.checkpoint)
            TrainingLogger.info(f"  saved checkpoint to {args.checkpoint}")

    torch.save({"net_state": net.state_dict(), "step": step}, args.checkpoint)


def main() -> None:
    args = parse_args()

    # Init resources
    TrainingLogger.setup(
        run_name="pretrain", console_level=getattr(logging, args.log_level)
    )
    os.makedirs(os.path.dirname(args.checkpoint) or ".", exist_ok=True)
    device = torch.device(args.device)

    # Custom board size and fleet config
    try:
        setup_board_and_fleet(args)
    except ValueError as e:
        raise e

    run_training_loop(args, device)

    TrainingLogger.info(f"Pretraining complete. Checkpoint: {args.checkpoint}")
    TrainingLogger.close()


if __name__ == "__main__":
    main()
