"""Vanilla DQN training for the Battleship Q-learning agent.

Usage:
    python training/q_learning/q_train.py
    python training/q_learning/q_train.py --episodes 100000 --save-path checkpoints/q_agent.pt
"""

from __future__ import annotations

import argparse
import copy
import os
import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from game.agents.q_net import QNetwork
from game.agents.q_net.state_encoder import BayesEncoder, legal_mask_from_obs
from training.battleship_env import BattleshipEnv
from training.q_learning.q_replay_buffer import ReplayBuffer
from training.q_learning.reward_fns import REWARD_REGISTRY, make_reward_fn
from training.training_logger import TrainingLogger

# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
EPISODES = 50_000
GAMMA = 0.99
LR = 1e-4
BATCH_SIZE = 64
BUFFER_CAP = 100_000
TARGET_SYNC = 500  # steps between target network syncs
EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY = 0.9999  # multiplicative per episode
EVAL_INTERVAL = 1_000  # episodes between evaluations
EVAL_GAMES = 200
DEFAULT_SAVE = "checkpoints/q_agent.pt"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", type=int, default=EPISODES)
    p.add_argument("--lr", type=float, default=LR)
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    p.add_argument("--buffer-cap", type=int, default=BUFFER_CAP)
    p.add_argument("--target-sync", type=int, default=TARGET_SYNC)
    p.add_argument("--eps-start", type=float, default=EPS_START)
    p.add_argument("--eps-end", type=float, default=EPS_END)
    p.add_argument("--eps-decay", type=float, default=EPS_DECAY)
    p.add_argument("--eval-interval", type=int, default=EVAL_INTERVAL)
    p.add_argument("--eval-games", type=int, default=EVAL_GAMES)
    p.add_argument("--save-path", type=str, default=DEFAULT_SAVE)
    p.add_argument("--resume", type=str, default=None,
                   help="Path to a checkpoint to resume training from")
    p.add_argument("--device", type=str, default="cpu")
    p.add_argument(
        "--reward-fn",
        default="default",
        choices=list(REWARD_REGISTRY),
        help=f"Reward function to use. Options: {list(REWARD_REGISTRY)}",
    )
    p.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Bayesian probability bonus scale factor (used by --reward-fn bayes)",
    )
    return p.parse_args()


def evaluate(net: QNetwork, n_games: int, device: torch.device) -> float:
    """Return mean turns-to-win over n_games episodes with greedy policy."""
    net.eval()
    env = BattleshipEnv()
    encoder = BayesEncoder()
    turns = []

    for _ in range(n_games):
        obs, _ = env.reset()
        encoder.reset()
        while not env.done:
            cell_np, global_np = encoder.encode(obs)
            legal = legal_mask_from_obs(obs)

            cell_t = torch.tensor(cell_np, dtype=torch.float32, device=device).unsqueeze(0)
            global_t = torch.tensor(global_np, dtype=torch.float32, device=device).unsqueeze(0)
            mask_t = torch.tensor(legal, dtype=torch.bool, device=device).unsqueeze(0)

            with torch.no_grad():
                q = net(cell_t, global_t, mask_t)
            action = q[0].argmax().item()
            obs, _, _, _, info = env.step(action)
            encoder.update(info["coordinate"], info["result"], info["ship_sunk"])
        turns.append(env.turn)

    net.train()
    return float(np.mean(turns))


def _save(
    path: str,
    online_net: QNetwork,
    target_net: QNetwork,
    optimizer: optim.Optimizer,
    episode: int,
    total_steps: int,
    epsilon: float,
    best_turns: float,
) -> None:
    torch.save(
        {
            "net_state": online_net.state_dict(),
            "target_net_state": target_net.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "episode": episode,
            "total_steps": total_steps,
            "epsilon": epsilon,
            "best_turns": best_turns,
        },
        path,
    )


def train(args: argparse.Namespace) -> None:
    TrainingLogger.setup(run_name="q_train")
    device = torch.device(args.device)

    online_net = QNetwork().to(device)
    target_net = copy.deepcopy(online_net)
    target_net.eval()

    optimizer = optim.Adam(online_net.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()
    buffer = ReplayBuffer(args.buffer_cap)
    env = BattleshipEnv()
    encoder = BayesEncoder()
    reward_fn = make_reward_fn(args.reward_fn, args.alpha)

    os.makedirs(os.path.dirname(args.save_path) or ".", exist_ok=True)

    start_episode = 1
    epsilon = args.eps_start
    total_steps = 0
    best_turns = float("inf")

    if args.resume:
        ckpt = torch.load(args.resume, map_location=device)
        online_net.load_state_dict(ckpt["net_state"])
        target_net.load_state_dict(ckpt.get("target_net_state", ckpt["net_state"]))
        if "optimizer_state" in ckpt:
            optimizer.load_state_dict(ckpt["optimizer_state"])
        start_episode = ckpt.get("episode", 1) + 1
        total_steps = ckpt.get("total_steps", 0)
        epsilon = ckpt.get("epsilon", args.eps_start)
        best_turns = ckpt.get("best_turns", float("inf"))
        TrainingLogger.info(f"Resumed from {args.resume} at episode {start_episode - 1}")

    TrainingLogger.info("Starting training...")

    for episode in range(start_episode, args.episodes + 1):
        print(f"Episode {episode}/{args.episodes} - Epsilon: {epsilon:.4f}", end="\r")
        obs, _ = env.reset()
        encoder.reset()
        cell_feats, global_feats = encoder.encode(obs)

        while not env.done:
            legal_mask = legal_mask_from_obs(obs)
            legal_indices = np.where(legal_mask)[0]

            # Epsilon-greedy action selection
            if random.random() < epsilon:
                action = int(random.choice(legal_indices))
            else:
                cell_t = torch.tensor(cell_feats, dtype=torch.float32, device=device).unsqueeze(0)
                global_t = torch.tensor(global_feats, dtype=torch.float32, device=device).unsqueeze(0)
                mask_t = torch.tensor(legal_mask, dtype=torch.bool, device=device).unsqueeze(0)
                with torch.no_grad():
                    q = online_net(cell_t, global_t, mask_t)
                action = int(q[0].argmax().item())

            next_obs, env_reward, done, _, info = env.step(action)
            reward = reward_fn(action, cell_feats, env_reward, info["result"], info["ship_sunk"], done)
            encoder.update(info["coordinate"], info["result"], info["ship_sunk"])
            if not done:
                next_cell_feats, next_global_feats = encoder.encode(next_obs)
                next_legal_mask = legal_mask_from_obs(next_obs)
            else:
                next_cell_feats = np.zeros_like(cell_feats)
                next_global_feats = np.zeros_like(global_feats)
                next_legal_mask = np.zeros(100, dtype=bool)

            buffer.push(
                cell_feats,
                global_feats,
                action,
                reward,
                next_cell_feats,
                next_global_feats,
                done,
                next_legal_mask,
            )

            obs = next_obs
            cell_feats = next_cell_feats
            global_feats = next_global_feats
            total_steps += 1

            # --- Learning step ---
            if len(buffer) >= args.batch_size:
                batch = buffer.sample(args.batch_size)
                b = {k: v.to(device) for k, v in batch.items()}

                # Current Q-values (no legal masking — we want the raw Q for the taken action)
                q_all = online_net(
                    b["cell_feats"],
                    b["global_feats"],
                    torch.ones(args.batch_size, 100, dtype=torch.bool, device=device),
                )
                q_pred = q_all.gather(1, b["actions"].unsqueeze(1)).squeeze(1)

                # Target Q-values (vanilla DQN)
                with torch.no_grad():
                    q_next = target_net(
                        b["next_cell_feats"],
                        b["next_global_feats"],
                        b["next_legal_mask"],
                    )
                    q_next_max = q_next.max(dim=1).values
                    td_target = b["rewards"] + args.gamma * q_next_max * (1.0 - b["dones"])

                loss = loss_fn(q_pred, td_target)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # --- Sync target network ---
            if total_steps % args.target_sync == 0:
                target_net.load_state_dict(online_net.state_dict())

        epsilon = max(args.eps_end, epsilon * args.eps_decay)

        # --- Periodic evaluation ---
        if episode % args.eval_interval == 0:
            mean_turns = evaluate(online_net, args.eval_games, device)
            TrainingLogger.info(
                f"ep={episode:6d}  eps={epsilon:.4f}  steps={total_steps:7d}  "
                f"mean_turns={mean_turns:.1f}"
            )
            _save(
                args.save_path + ".latest",
                online_net, target_net, optimizer,
                episode, total_steps, epsilon, best_turns,
            )
            if mean_turns < best_turns:
                best_turns = mean_turns
                _save(
                    args.save_path,
                    online_net, target_net, optimizer,
                    episode, total_steps, epsilon, best_turns,
                )
                TrainingLogger.info(
                    f"checkpoint saved -> {args.save_path} (best={best_turns:.1f})"
                )


def main() -> None:
    args = parse_args()
    args.gamma = GAMMA
    train(args)


if __name__ == "__main__":
    main()
