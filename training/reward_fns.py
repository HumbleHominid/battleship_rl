from __future__ import annotations

from typing import Callable, Optional

import numpy as np

from training.training_logger import TrainingLogger

# (action, pre_shot_cell_feats (100,1) | None, base_reward, result, ship_sunk, done) -> float
RewardFn = Callable[[int, Optional[np.ndarray], float, str, Optional[str], bool], float]


def default_reward(
    action: int,
    cell_feats: Optional[np.ndarray],
    base_reward: float,
    result: str,
    ship_sunk: Optional[str],
    done: bool,
) -> float:
    return base_reward


def bayes_augment_reward(alpha: float) -> RewardFn:
    """Return a reward fn that adds alpha * Bayesian probability of the chosen cell.

    The probability is taken from cell_feats[action, 0], the normalized total
    Bayesian occupancy for the selected cell before the shot was taken.
    Requires pre_shot_cell_feats to be passed to env.step().
    """

    def _fn(
        action: int,
        cell_feats: Optional[np.ndarray],
        base_reward: float,
        result: str,
        ship_sunk: Optional[str],
        done: bool,
    ) -> float:
        if cell_feats is None:
            raise ValueError(
                "bayes reward fn requires pre_shot_cell_feats — pass cell_feats to env.step()"
            )
        TrainingLogger.debug(
            f"Bayes reward: base {base_reward:.2f} + alpha {alpha} * prob {cell_feats[action, 0]:.4f}"
        )
        return base_reward + alpha * float(cell_feats[action, 0])

    return _fn


REWARD_REGISTRY: dict[str, str] = {
    "default": "Outcome-based rewards only (hit/miss/sunk/win)",
    "bayes": "Outcome rewards augmented with Bayesian probability bonus",
}


def make_reward_fn(name: str, alpha: float = 0.5) -> RewardFn:
    """Instantiate a reward function by name.

    Args:
        name:  Key from REWARD_REGISTRY.
        alpha: Scaling factor for parameterized reward fns (e.g. 'bayes').
    """
    if name == "default":
        return default_reward
    if name == "bayes":
        return bayes_augment_reward(alpha)
    raise ValueError(f"Unknown reward fn: {name!r}. Options: {list(REWARD_REGISTRY)}")
