from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class Transition:
    cell_feats: np.ndarray       # (100, 3)
    global_feats: np.ndarray     # (2,)
    action: int
    reward: float
    next_cell_feats: np.ndarray  # (100, 3)
    next_global_feats: np.ndarray  # (2,)
    done: bool
    next_legal_mask: np.ndarray  # (100,) bool


class ReplayBuffer:
    """Circular experience replay buffer for DQN training."""

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._buf: list[Transition] = []
        self._pos = 0

    def push(
        self,
        cell_feats: np.ndarray,
        global_feats: np.ndarray,
        action: int,
        reward: float,
        next_cell_feats: np.ndarray,
        next_global_feats: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        t = Transition(
            cell_feats=cell_feats,
            global_feats=global_feats,
            action=action,
            reward=reward,
            next_cell_feats=next_cell_feats,
            next_global_feats=next_global_feats,
            done=done,
            next_legal_mask=next_legal_mask,
        )
        if len(self._buf) < self._capacity:
            self._buf.append(t)
        else:
            self._buf[self._pos] = t
        self._pos = (self._pos + 1) % self._capacity

    def sample(self, batch_size: int) -> dict[str, torch.Tensor]:
        batch = random.sample(self._buf, batch_size)
        return {
            "cell_feats": torch.tensor(
                np.stack([t.cell_feats for t in batch]), dtype=torch.float32
            ),
            "global_feats": torch.tensor(
                np.stack([t.global_feats for t in batch]), dtype=torch.float32
            ),
            "actions": torch.tensor(
                [t.action for t in batch], dtype=torch.long
            ),
            "rewards": torch.tensor(
                [t.reward for t in batch], dtype=torch.float32
            ),
            "next_cell_feats": torch.tensor(
                np.stack([t.next_cell_feats for t in batch]), dtype=torch.float32
            ),
            "next_global_feats": torch.tensor(
                np.stack([t.next_global_feats for t in batch]), dtype=torch.float32
            ),
            "dones": torch.tensor(
                [t.done for t in batch], dtype=torch.float32
            ),
            "next_legal_mask": torch.tensor(
                np.stack([t.next_legal_mask for t in batch]), dtype=torch.bool
            ),
        }

    def __len__(self) -> int:
        return len(self._buf)
