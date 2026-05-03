import random

from game.agents.base_agent import BaseAgent
from game.game_board import GameBoard


class RandomAgent(BaseAgent):
    def __init__(self) -> None:
        self._untried_cells: list[tuple[int, int]] = [
            (r, c) for r in range(10) for c in range(10)
        ]
        self._rng = random.Random()

    def select_move(self, obs: dict) -> str:
        if not self._untried_cells:
            raise RuntimeError("No untried cells remain")
        cell = self._rng.choice(self._untried_cells)
        self._untried_cells.remove(cell)
        return GameBoard.format_coordinate(cell[0], cell[1])

    def reset(self) -> None:
        self._untried_cells = [(r, c) for r in range(10) for c in range(10)]
