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
from training.q_replay_buffer import ReplayBuffer
from training.reward_fns import REWARD_REGISTRY, make_reward_fn
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
    p.add_argument("--gamma", type=float, default=GAMMA)
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
    p.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to a checkpoint to resume training from",
    )
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
    p.add_argument(
        "--demo-games",
        type=int,
        default=0,
        help="Bayesian agent games to pre-load into the replay buffer (0 = skip)",
    )
    p.add_argument(
        "--pretrain-games",
        type=int,
        default=0,
        help="Games of random play to collect for supervised pretraining (0 = skip)",
    )
    p.add_argument(
        "--pretrain-epochs",
        type=int,
        default=10,
        help="Epochs over the pretraining dataset",
    )
    p.add_argument(
        "--placement-method",
        type=str,
        default="mix",
        help="Placement method for training: 'mix' (samples from all available options including cognitive_human), 'random', 'cognitive_human', etc."
    )
    p.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )
    return p.parse_args()


def evaluate(
    net: QNetwork,
    n_games: int,
    device: torch.device,
    placement_method: str = "mix",
) -> float:
    """Return mean turns-to-win over n_games episodes with greedy policy."""
    net.eval()
    env = BattleshipEnv(placement_method=placement_method)
    encoder = BayesEncoder()
    turns = []

    for _ in range(n_games):
        obs, _ = env.reset()
        encoder.reset()
        while not env.done:
            cell_np, global_np = encoder.encode(obs)
            legal = legal_mask_from_obs(obs)

            cell_t = torch.tensor(
                cell_np, dtype=torch.float32, device=device
            ).unsqueeze(0)
            global_t = torch.tensor(
                global_np, dtype=torch.float32, device=device
            ).unsqueeze(0)
            mask_t = torch.tensor(legal, dtype=torch.bool, device=device).unsqueeze(0)

            with torch.no_grad():
                q = net(cell_t, global_t, mask_t)
            action = q[0].argmax().item()
            obs, _, _, _, info = env.step(action)
            encoder.update(info["coordinate"], info["result"], info["ship_sunk"])
        turns.append(env.turn)

    net.train()
    return float(np.mean(turns))


def pretrain_supervised(
    net: QNetwork,
    n_games: int,
    n_epochs: int,
    batch_size: int,
    lr: float,
    device: torch.device,
    placement_method: str = "mix",
) -> None:
    """Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].

    Plays n_games with random actions to generate diverse board states, then
    trains the network for n_epochs so that Q-values track Bayesian probability
    before any RL updates begin.
    """
    TrainingLogger.info("Pretraining: collecting %d games...", n_games)
    env = BattleshipEnv(placement_method=placement_method)
    encoder = BayesEncoder()

    demos: list[tuple[np.ndarray, np.ndarray]] = []
    for _ in range(n_games):
        obs, _ = env.reset()
        encoder.reset()
        while not env.done:
            cell_feats, global_feats = encoder.encode(obs)
            demos.append((cell_feats.copy(), global_feats.copy()))
            action = random.choice(env.legal_actions())
            obs, _, _, _, info = env.step(action)
            encoder.update(info["coordinate"], info["result"], info["ship_sunk"])

    TrainingLogger.info("Pretraining: %d samples, %d epochs", len(demos), n_epochs)
    optimizer = optim.Adam(net.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    all_mask = torch.ones(1, 100, dtype=torch.bool, device=device)
    min_loss = 1e-4

    net.train()
    for epoch in range(1, n_epochs + 1):
        random.shuffle(demos)
        total_loss = 0.0
        steps = 0
        for i in range(0, len(demos), batch_size):
            chunk = demos[i : i + batch_size]
            cell_t = torch.tensor(
                np.stack([c for c, _ in chunk]), dtype=torch.float32, device=device
            )
            global_t = torch.tensor(
                np.stack([g for _, g in chunk]), dtype=torch.float32, device=device
            )
            target = cell_t[:, :, 0]  # (B, 100) — channel 0 is Bayesian probability
            mask = all_mask.expand(len(chunk), -1)
            q = net(cell_t, global_t, mask)
            loss = loss_fn(q, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            steps += 1
        loss = total_loss / steps
        TrainingLogger.info("Pretrain epoch %d/%d  loss=%.5f", epoch, n_epochs, loss)
        if loss < min_loss:
            TrainingLogger.info(
                "Pretrain loss %.5f < %.5f, stopping early", loss, min_loss
            )
            break


def fill_demo_buffer(
    buffer: ReplayBuffer,
    n_games: int,
    reward_fn,
    placement_method: str = "mix",
) -> None:
    """Pre-populate replay buffer with Bayesian agent game transitions."""
    from game.agents.bayesian_agent import BayesianAgent
    from game.coordinate_methods import parse_coordinate
    from game.models import Board

    TrainingLogger.info("Demo buffer: collecting %d Bayesian games...", n_games)
    env = BattleshipEnv(reward_fn=reward_fn, placement_method=placement_method)
    encoder = BayesEncoder()
    agent = BayesianAgent(deterministic_selection=False)

    for _ in range(n_games):
        obs, _ = env.reset()
        encoder.reset()
        agent.reset()
        cell_feats, global_feats = encoder.encode(obs)

        while not env.done:
            coord = agent.select_move(obs)
            row, col = parse_coordinate(coord)
            action = row * Board.board_size + col

            next_obs, reward, done, _, info = env.step(action, cell_feats)
            encoder.update(info["coordinate"], info["result"], info["ship_sunk"])
            agent.receive_result(info["coordinate"], info["result"], info["ship_sunk"])

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

    TrainingLogger.info("Demo buffer: %d transitions loaded", len(buffer))


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
    # Limit PyTorch to a single thread to avoid thread overhead on CPU
    torch.set_num_threads(1)
    
    device = torch.device(args.device)

    online_net = QNetwork().to(device)
    target_net = copy.deepcopy(online_net)
    target_net.eval()

    optimizer = optim.Adam(online_net.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()
    buffer = ReplayBuffer(args.buffer_cap)
    reward_fn = make_reward_fn(args.reward_fn, args.alpha)
    env = BattleshipEnv(reward_fn=reward_fn, placement_method=args.placement_method)
    encoder = BayesEncoder()
    reward = 0.0

    os.makedirs(os.path.dirname(args.save_path) or ".", exist_ok=True)

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
        TrainingLogger.info(
            f"Resumed from {args.resume} at episode {start_episode - 1}"
        )
    else:
        start_episode = 1
        epsilon = args.eps_start
        total_steps = 0
        best_turns = float("inf")

    if not args.resume and args.pretrain_games > 0:
        pretrain_supervised(
            online_net,
            args.pretrain_games,
            args.pretrain_epochs,
            args.batch_size,
            args.lr,
            device,
            placement_method=args.placement_method,
        )
        target_net.load_state_dict(online_net.state_dict())

    if not args.resume and args.demo_games > 0:
        fill_demo_buffer(buffer, args.demo_games, reward_fn, placement_method=args.placement_method)

    TrainingLogger.info("Starting training...")

    for episode in range(start_episode, args.episodes + 1):
        print(
            f"ep: {episode}/{args.episodes} - eps: {epsilon:.4f} - reward: {reward:.4f}",
            end="\r",
        )
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
                cell_t = torch.tensor(
                    cell_feats, dtype=torch.float32, device=device
                ).unsqueeze(0)
                global_t = torch.tensor(
                    global_feats, dtype=torch.float32, device=device
                ).unsqueeze(0)
                mask_t = torch.tensor(
                    legal_mask, dtype=torch.bool, device=device
                ).unsqueeze(0)
                with torch.no_grad():
                    q = online_net(cell_t, global_t, mask_t)
                action = int(q[0].argmax().item())

            next_obs, reward, done, _, info = env.step(action, cell_feats)
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

                # Target Q-values (Double DQN)
                with torch.no_grad():
                    # Select actions using online_net (with legal mask)
                    q_next_online = online_net(
                        b["next_cell_feats"],
                        b["next_global_feats"],
                        b["next_legal_mask"],
                    )
                    best_next_actions = q_next_online.argmax(dim=1)

                    # Evaluate those actions using target_net (with legal mask)
                    q_next_target = target_net(
                        b["next_cell_feats"],
                        b["next_global_feats"],
                        b["next_legal_mask"],
                    )
                    q_next_selected = q_next_target.gather(1, best_next_actions.unsqueeze(1)).squeeze(1)

                    td_target = b["rewards"] + args.gamma * q_next_selected * (
                        1.0 - b["dones"]
                    )

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
            mean_turns = evaluate(
                online_net,
                args.eval_games,
                device,
                placement_method=args.placement_method,
            )
            TrainingLogger.info(
                f"ep={episode}  eps={epsilon:.4f}  steps={total_steps}  "
                f"mean_turns={mean_turns:.1f}"
            )
            _save(
                args.save_path + ".latest",
                online_net,
                target_net,
                optimizer,
                episode,
                total_steps,
                epsilon,
                best_turns,
            )
            if mean_turns < best_turns:
                best_turns = mean_turns
                _save(
                    args.save_path,
                    online_net,
                    target_net,
                    optimizer,
                    episode,
                    total_steps,
                    epsilon,
                    best_turns,
                )
                TrainingLogger.info(
                    f"checkpoint saved -> {args.save_path} (best={best_turns:.1f})"
                )


def main() -> None:
    args = parse_args()
    TrainingLogger.setup(run_name="q_train", console_level=args.log_level)
    train(args)


if __name__ == "__main__":
    main()
