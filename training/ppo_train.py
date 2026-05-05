"""PPO fine-tuning for the TransformerPPO Battleship agent.

Collects on-policy rollouts using serial episode collection, then updates
the policy and value networks with clipped PPO.

Usage:
    python training/ppo_train.py --iters 500 --checkpoint checkpoints/pretrain.pt
    python training/ppo_train.py --iters 1000 --from-scratch
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from game.agents.bayesian_agent import BayesianAgent
from game.agents.feature_extractor import FeatureExtractor
from game.agents.transformer_ppo_agent import TransformerPPONet
from game.coordinate_methods import parse_coordinate
from game.models import Board
from training.battleship_env import BattleshipEnv
from training.training_logger import TrainingLogger

# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
GAMMA = 0.99
LAM = 0.95  # GAE lambda
CLIP_EPS = 0.2
VALUE_COEF = 0.5
ENTROPY_COEF = 0.01
MAX_GRAD_NORM = 0.5
N_EPOCHS = 4  # PPO update epochs per rollout
MINIBATCH = 256  # transitions per minibatch
N_EPISODES_PER_ITER = 8


@dataclass
class Transition:
    cell_feats: np.ndarray  # (100, CELL_FEATURE_DIM)
    global_feats: np.ndarray  # (GLOBAL_FEATURE_DIM,)
    legal_mask: np.ndarray  # (100,) bool
    action: int
    reward: float
    done: bool
    log_prob: float
    value: float


@dataclass
class RolloutBuffer:
    transitions: list[Transition] = field(default_factory=list)

    def add(self, t: Transition) -> None:
        self.transitions.append(t)

    def compute_returns_advantages(
        self, gamma: float, lam: float
    ) -> tuple[np.ndarray, np.ndarray]:
        n = len(self.transitions)
        returns = np.zeros(n, dtype=np.float32)
        advantages = np.zeros(n, dtype=np.float32)
        gae = 0.0

        for i in reversed(range(n)):
            t = self.transitions[i]
            next_value = (
                0.0 if t.done else (self.transitions[i + 1].value if i + 1 < n else 0.0)
            )
            delta = t.reward + gamma * next_value * (1 - float(t.done)) - t.value
            gae = delta + gamma * lam * (1 - float(t.done)) * gae
            advantages[i] = gae
            returns[i] = gae + t.value

        return returns, advantages

    def to_tensors(self, device: torch.device) -> dict[str, torch.Tensor]:
        n = len(self.transitions)
        cell = np.stack([t.cell_feats for t in self.transitions])  # (N, 100, F)
        glob = np.stack([t.global_feats for t in self.transitions])  # (N, G)
        mask = np.stack([t.legal_mask for t in self.transitions])  # (N, 100)
        actions = np.array([t.action for t in self.transitions])  # (N,)
        old_lp = np.array([t.log_prob for t in self.transitions])  # (N,)

        returns, advantages = self.compute_returns_advantages(GAMMA, LAM)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        return {
            "cell": torch.tensor(cell, dtype=torch.float32, device=device),
            "glob": torch.tensor(glob, dtype=torch.float32, device=device),
            "mask": torch.tensor(mask, dtype=torch.bool, device=device),
            "actions": torch.tensor(actions, dtype=torch.long, device=device),
            "old_log_probs": torch.tensor(old_lp, dtype=torch.float32, device=device),
            "returns": torch.tensor(returns, dtype=torch.float32, device=device),
            "advantages": torch.tensor(advantages, dtype=torch.float32, device=device),
        }


def coord_to_index(coord: str) -> int:
    row, col = parse_coordinate(coord)
    return row * Board.board_size + col


def collect_episode(
    net: TransformerPPONet,
    env: BattleshipEnv,
    extractor: FeatureExtractor,
    device: torch.device,
) -> tuple[list[Transition], int]:
    """Run one episode, collecting transitions. Returns (transitions, turns_to_win)."""
    obs, _ = env.reset()
    extractor.reset()
    transitions: list[Transition] = []

    while not env.done:
        cell_np = extractor.compute_cell_features(obs)
        global_np = extractor.compute_global_features(
            obs["ships_sunk"]["by_you"], obs["turn"]
        )

        cell_t = torch.tensor(cell_np, dtype=torch.float32, device=device).unsqueeze(0)
        global_t = torch.tensor(
            global_np, dtype=torch.float32, device=device
        ).unsqueeze(0)
        legal_mask = cell_t[0, :, 12].bool().unsqueeze(0)

        with torch.no_grad():
            log_probs, value = net(cell_t, global_t, legal_mask)

        # Sample action from distribution
        probs = log_probs[0].exp()
        action = torch.multinomial(probs, 1).item()
        log_prob = log_probs[0, action].item()

        obs, reward, done, _, info = env.step(action)
        extractor.update(info["coordinate"], info["result"], info["ship_sunk"])

        transitions.append(
            Transition(
                cell_feats=cell_np,
                global_feats=global_np,
                legal_mask=cell_t[0, :, 12].cpu().numpy().astype(bool),
                action=action,
                reward=reward,
                done=done,
                log_prob=log_prob,
                value=value[0].item(),
            )
        )

    return transitions, env.turn


def ppo_update(
    net: TransformerPPONet,
    optimizer: optim.Optimizer,
    batch: dict[str, torch.Tensor],
) -> dict[str, float]:
    n = batch["cell"].shape[0]
    indices = torch.randperm(n, device=batch["cell"].device)

    total_policy_loss = total_value_loss = total_entropy = 0.0
    n_updates = 0

    for start in range(0, n, MINIBATCH):
        idx = indices[start : start + MINIBATCH]
        cell = batch["cell"][idx]
        glob = batch["glob"][idx]
        mask = batch["mask"][idx]
        actions = batch["actions"][idx]
        old_lp = batch["old_log_probs"][idx]
        returns = batch["returns"][idx]
        advs = batch["advantages"][idx]

        log_probs, value = net(cell, glob, mask)
        new_lp = log_probs.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Clipped PPO objective
        ratio = (new_lp - old_lp).exp()
        surr1 = ratio * advs
        surr2 = ratio.clamp(1 - CLIP_EPS, 1 + CLIP_EPS) * advs
        policy_loss = -torch.min(surr1, surr2).mean()

        # Value loss (clipped)
        value_loss = nn.functional.mse_loss(value, returns)

        # Entropy bonus (over legal actions only; clamp avoids 0 * -inf = NaN)
        probs = log_probs.exp()
        entropy = -(probs * log_probs.clamp(min=-100)).sum(dim=-1).mean()

        loss = policy_loss + VALUE_COEF * value_loss - ENTROPY_COEF * entropy
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(net.parameters(), MAX_GRAD_NORM)
        optimizer.step()

        total_policy_loss += policy_loss.item()
        total_value_loss += value_loss.item()
        total_entropy += entropy.item()
        n_updates += 1

    k = max(n_updates, 1)
    return {
        "policy_loss": total_policy_loss / k,
        "value_loss": total_value_loss / k,
        "entropy": total_entropy / k,
    }


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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--iters", type=int, default=500)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Path to a pretrained checkpoint to load",
    )
    p.add_argument(
        "--from-scratch", action="store_true", help="Train from random initialization"
    )
    p.add_argument("--save-path", type=str, default="checkpoints/ppo_best.pt")
    p.add_argument("--eval-interval", type=int, default=25)
    p.add_argument("--eval-games", type=int, default=100)
    p.add_argument("--device", type=str, default="cpu")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device(args.device)
    os.makedirs(os.path.dirname(args.save_path) or ".", exist_ok=True)

    TrainingLogger.setup(run_name="ppo")

    net = TransformerPPONet().to(device)
    if not args.from_scratch and args.checkpoint:
        ckpt = torch.load(args.checkpoint, map_location=device)
        net.load_state_dict(ckpt["net_state"])
        TrainingLogger.info(f"Loaded checkpoint from {args.checkpoint}")
    net.train()

    optimizer = optim.Adam(net.parameters(), lr=args.lr)

    TrainingLogger.info("Computing BayesianAgent baseline (100 games)...")
    baseline = bayes_baseline(100)
    TrainingLogger.info(f"Baseline (BayesianAgent): {baseline:.2f} turns avg")

    best_turns = float("inf")
    env = BattleshipEnv()
    extractor = FeatureExtractor()

    for iteration in range(1, args.iters + 1):
        t0 = time.time()
        buffer = RolloutBuffer()
        episode_turns = []

        for _ in range(N_EPISODES_PER_ITER):
            transitions, turns = collect_episode(net, env, extractor, device)
            for t in transitions:
                buffer.add(t)
            episode_turns.append(turns)

        batch = buffer.to_tensors(device)

        losses: dict[str, float] = {}
        for _ in range(N_EPOCHS):
            losses = ppo_update(net, optimizer, batch)

        elapsed = time.time() - t0
        mean_turns = float(np.mean(episode_turns))
        TrainingLogger.info(
            f"iter {iteration:4d} | turns {mean_turns:.1f} | "
            f"policy {losses['policy_loss']:.4f} | "
            f"value {losses['value_loss']:.4f} | "
            f"entropy {losses['entropy']:.4f} | {elapsed:.2f}s"
        )

        if iteration % args.eval_interval == 0:
            eval_turns = evaluate(net, args.eval_games, device)
            delta = baseline - eval_turns
            TrainingLogger.info(
                f"  eval {args.eval_games} games: {eval_turns:.2f} turns "
                f"(baseline Δ {delta:+.2f})"
            )
            if eval_turns < best_turns:
                best_turns = eval_turns
                torch.save(
                    {"net_state": net.state_dict(), "iter": iteration}, args.save_path
                )
                TrainingLogger.info(
                    f"  *** new best {best_turns:.2f} — saved to {args.save_path}"
                )

    TrainingLogger.info(
        f"\nTraining complete. Best eval: {best_turns:.2f} turns. Baseline: {baseline:.2f} turns."
    )
    TrainingLogger.close()


if __name__ == "__main__":
    main()
