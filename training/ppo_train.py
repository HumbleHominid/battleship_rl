"""PPO fine-tuning for the TransformerPPO Battleship agent.

Collects on-policy rollouts using serial episode collection, then updates
the policy and value networks with clipped PPO.

Usage:
    python training/ppo_train.py --iters 500 --checkpoint checkpoints/pretrain.pt
    python training/ppo_train.py --iters 1000 --from-scratch
"""

from __future__ import annotations

import argparse
import logging
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

    def to_tensors(
        self, device: torch.device, gamma: float, lam: float
    ) -> dict[str, torch.Tensor]:
        cell = np.stack([t.cell_feats for t in self.transitions])  # (N, 100, F)
        glob = np.stack([t.global_feats for t in self.transitions])  # (N, G)
        mask = np.stack([t.legal_mask for t in self.transitions])  # (N, 100)
        actions = np.array([t.action for t in self.transitions])  # (N,)
        old_lp = np.array([t.log_prob for t in self.transitions])  # (N,)

        returns, advantages = self.compute_returns_advantages(gamma, lam)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
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
    policy_optimizer: optim.Optimizer,
    value_optimizer: optim.Optimizer,
    policy_params: list,
    value_params: list,
    batch: dict[str, torch.Tensor],
    clip_eps: float,
    entropy_coef: float,
    max_grad_norm: float,
    minibatch: int,
) -> dict[str, float]:
    n = batch["cell"].shape[0]
    indices = torch.randperm(n, device=batch["cell"].device)

    total_policy_loss = total_value_loss = total_entropy = 0.0
    n_updates = 0

    for start in range(0, n, minibatch):
        idx = indices[start : start + minibatch]
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
        surr2 = ratio.clamp(1 - clip_eps, 1 + clip_eps) * advs
        policy_loss = -torch.min(surr1, surr2).mean()

        # Entropy bonus (over legal actions only; clamp avoids 0 * -inf = NaN)
        probs = log_probs.exp()
        entropy = -(probs * log_probs.clamp(min=-100)).sum(dim=-1).mean()

        # Value loss
        value_loss = nn.functional.mse_loss(value, returns)

        # Policy trunk update (retain graph so value backward can follow)
        policy_optimizer.zero_grad()
        (policy_loss - entropy_coef * entropy).backward(retain_graph=True)
        nn.utils.clip_grad_norm_(policy_params, max_grad_norm)
        policy_optimizer.step()

        # Value trunk update (independent backward — no policy gradient)
        value_optimizer.zero_grad()
        value_loss.backward()
        nn.utils.clip_grad_norm_(value_params, max_grad_norm)
        value_optimizer.step()

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


def value_warmup_update(
    net: TransformerPPONet,
    value_optimizer: optim.Optimizer,
    value_params: list,
    batch: dict[str, torch.Tensor],
    max_grad_norm: float,
    minibatch: int,
) -> float:
    """One epoch of value-trunk-only updates — policy trunk receives zero gradient."""
    n = batch["cell"].shape[0]
    indices = torch.randperm(n, device=batch["cell"].device)
    total_value_loss = 0.0
    n_updates = 0

    for start in range(0, n, minibatch):
        TrainingLogger.debug(
            f"    Update {start // minibatch + 1} / {n // minibatch + (n % minibatch > 0)}"
        )
        idx = indices[start : start + minibatch]
        _, value = net(batch["cell"][idx], batch["glob"][idx], batch["mask"][idx])
        value_loss = nn.functional.mse_loss(value, batch["returns"][idx])
        value_optimizer.zero_grad()
        value_loss.backward()
        nn.utils.clip_grad_norm_(value_params, max_grad_norm)
        value_optimizer.step()
        total_value_loss += value_loss.item()
        n_updates += 1

    return total_value_loss / max(n_updates, 1)


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
    # Training control
    p.add_argument("--iters", type=int, default=500)
    p.add_argument("--policy-lr", type=float, default=1e-4)
    p.add_argument("--value-lr", type=float, default=1e-4)
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
    # Value head warmup
    p.add_argument("--value-warmup-iters", type=int, default=100)
    # Rollout
    p.add_argument("--n-episodes-per-iter", type=int, default=32)
    # PPO update
    p.add_argument("--n-epochs", type=int, default=2)
    p.add_argument("--minibatch", type=int, default=512)
    p.add_argument("--gamma", type=float, default=0.99)
    p.add_argument("--lam", type=float, default=0.95)
    p.add_argument("--clip-eps", type=float, default=0.15)
    p.add_argument("--entropy-coef", type=float, default=0.003)
    p.add_argument("--max-grad-norm", type=float, default=0.5)
    p.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device(args.device)
    os.makedirs(os.path.dirname(args.save_path) or ".", exist_ok=True)

    TrainingLogger.setup(run_name="ppo", console_level=getattr(logging, args.log_level))

    net = TransformerPPONet().to(device)
    if not args.from_scratch and args.checkpoint:
        ckpt = torch.load(args.checkpoint, map_location=device)
        result = net.load_state_dict(ckpt["net_state"], strict=False)
        if result.missing_keys:
            TrainingLogger.warn(
                f"Checkpoint has {len(result.missing_keys)} missing keys "
                f"(architecture changed — re-run pretrain.py to get a compatible checkpoint). "
                f"First missing: {result.missing_keys[0]}"
            )
        else:
            TrainingLogger.info(f"Loaded checkpoint from {args.checkpoint}")
    net.train()

    policy_params = (
        list(net.policy_cell_proj.parameters())
        + list(net.policy_encoder.parameters())
        + list(net.policy_head.parameters())
    )
    value_params = (
        list(net.value_cell_proj.parameters())
        + list(net.global_proj.parameters())
        + [net.global_embed]
        + list(net.value_encoder.parameters())
        + list(net.value_head.parameters())
    )
    policy_optimizer = optim.Adam(policy_params, lr=args.policy_lr)
    value_optimizer = optim.Adam(value_params, lr=args.value_lr)

    n_baseline_games = 1000
    TrainingLogger.info(
        f"Computing BayesianAgent baseline ({n_baseline_games} games)..."
    )
    baseline = bayes_baseline(n_baseline_games)
    TrainingLogger.info(f"Baseline (BayesianAgent): {baseline:.2f} turns avg")

    best_turns = float("inf")
    env = BattleshipEnv()
    extractor = FeatureExtractor()

    if args.value_warmup_iters > 0:
        TrainingLogger.info(f"Value head warmup ({args.value_warmup_iters} iters)...")
        warmup_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            value_optimizer, T_max=args.value_warmup_iters, eta_min=args.value_lr * 0.01
        )
        for wu in range(1, args.value_warmup_iters + 1):
            TrainingLogger.debug(f"Warmup iteration {wu} / {args.value_warmup_iters}")
            buffer = RolloutBuffer()
            for _ in range(args.n_episodes_per_iter):
                transitions, _ = collect_episode(net, env, extractor, device)
                for t in transitions:
                    buffer.add(t)
            batch = buffer.to_tensors(device, gamma=args.gamma, lam=args.lam)
            for i in range(args.n_epochs):
                TrainingLogger.debug(f"  Epoch {i + 1} / {args.n_epochs}")
                v_loss = value_warmup_update(
                    net,
                    value_optimizer,
                    value_params,
                    batch,
                    args.max_grad_norm,
                    args.minibatch,
                )
            warmup_scheduler.step()

            current_lr = warmup_scheduler.get_last_lr()[0]
            msg = f"Value warmup iter {wu:4d}/{args.value_warmup_iters} | value loss {v_loss:.4f} | lr {current_lr:.2e}"
            if wu % 5 == 0:
                TrainingLogger.info(
                    f"  warmup {wu:4d}/{args.value_warmup_iters} | value {v_loss:.4f} | lr {current_lr:.2e}"
                )
            else:
                print(msg, end="\r")
        # Reset value LR to base rate for main PPO loop
        for pg in value_optimizer.param_groups:
            pg["lr"] = args.value_lr
        TrainingLogger.info("Value warmup complete.")

    for iteration in range(1, args.iters + 1):
        t0 = time.time()
        buffer = RolloutBuffer()
        episode_turns = []

        for _ in range(args.n_episodes_per_iter):
            transitions, turns = collect_episode(net, env, extractor, device)
            for t in transitions:
                buffer.add(t)
            episode_turns.append(turns)

        batch = buffer.to_tensors(device, gamma=args.gamma, lam=args.lam)

        losses: dict[str, float] = {}
        for _ in range(args.n_epochs):
            losses = ppo_update(
                net,
                policy_optimizer,
                value_optimizer,
                policy_params,
                value_params,
                batch,
                clip_eps=args.clip_eps,
                entropy_coef=args.entropy_coef,
                max_grad_norm=args.max_grad_norm,
                minibatch=args.minibatch,
            )

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
