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


def make_human_biased_reward(beta: float = 0.5) -> RewardFn:
    """Return a reward fn that adds beta * P_human[row][col] to the base reward.

    Precomputes the 10x10 density matrix using 2,000 simulations of cognitive_human placement.
    """
    import logging
    from game.game_logger import GameLogger
    GameLogger.setup(console_level=logging.WARNING)

    from game.game_board import GameBoard
    from game.models import Board, ShipType

    TrainingLogger.info(
        "Compiling empirical cognitive human density prior for reward shaping (2000 simulations)..."
    )
    density_grid = [[0.0] * Board.board_size for _ in range(Board.board_size)]

    for _ in range(2000):
        board = GameBoard()
        board.place_fleet("cognitive_human")
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                ship_type, _ = board.board.get_cell(r, c)
                if ship_type != ShipType.NONE:
                    density_grid[r][c] += 1.0

    total_density = sum(sum(row) for row in density_grid)
    avg_density = total_density / (Board.board_size * Board.board_size)
    for r in range(Board.board_size):
        for c in range(Board.board_size):
            density_grid[r][c] /= avg_density

    def _fn(
        action: int,
        cell_feats: Optional[np.ndarray],
        base_reward: float,
        result: str,
        ship_sunk: Optional[str],
        done: bool,
    ) -> float:
        row, col = divmod(action, Board.board_size)
        bonus = beta * density_grid[row][col]
        return base_reward + bonus

    return _fn


# Update registry and factory
REWARD_REGISTRY: dict[str, str] = {
    "default": "Outcome-based rewards only (hit/miss/sunk/win)",
    "bayes": "Outcome rewards augmented with Bayesian probability bonus",
    "human-biased": "Outcome rewards augmented with cognitive human placement density bonus",
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
    if name == "human-biased":
        return make_human_biased_reward(beta=alpha)
    raise ValueError(f"Unknown reward fn: {name!r}. Options: {list(REWARD_REGISTRY)}")

