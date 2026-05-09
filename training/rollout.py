from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch

from game.agents.feature_extractor import FeatureExtractor
from game.agents.ppo_net import TransformerPPONet
from training.battleship_env import BattleshipEnv


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
        old_values = np.array([t.value for t in self.transitions])  # (N,)

        returns, advantages = self.compute_returns_advantages(gamma, lam)
        # Normalize advantages only — returns stay raw so value head learns real scale.
        # Clamp std floor to prevent explosion when all episodes have similar length.
        adv_std = max(float(advantages.std()), 0.5)
        advantages = (advantages - advantages.mean()) / adv_std

        return {
            "cell": torch.tensor(cell, dtype=torch.float32, device=device),
            "glob": torch.tensor(glob, dtype=torch.float32, device=device),
            "mask": torch.tensor(mask, dtype=torch.bool, device=device),
            "actions": torch.tensor(actions, dtype=torch.long, device=device),
            "old_log_probs": torch.tensor(old_lp, dtype=torch.float32, device=device),
            "old_values": torch.tensor(old_values, dtype=torch.float32, device=device),
            "returns": torch.tensor(returns, dtype=torch.float32, device=device),
            "advantages": torch.tensor(advantages, dtype=torch.float32, device=device),
        }


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
