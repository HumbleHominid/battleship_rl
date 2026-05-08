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

import numpy as np
import torch
import torch.optim as optim

from game.agents.feature_extractor import FeatureExtractor
from game.agents.ppo_net import TransformerPPONet
from training.battleship_env import BattleshipEnv
from training.evaluate import bayes_baseline, evaluate
from training.ppo_update import ppo_update, value_warmup_update
from training.rollout import RolloutBuffer, collect_episode
from training.training_logger import TrainingLogger


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    # Training control
    p.add_argument("--iters", type=int, default=500)
    p.add_argument("--policy-lr", type=float, default=1e-4)
    p.add_argument("--value-lr", type=float, default=3e-4)
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
    p.add_argument("--n-value-epochs", type=int, default=4)
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

    policy_params = net.policy_params()
    value_params = net.value_params()
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
                n_value_epochs=args.n_value_epochs,
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
