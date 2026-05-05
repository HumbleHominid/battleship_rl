import random

from game.agents.base_agent import BaseAgent
from game.coordinate_methods import format_coordinate
from game.logger import GameLogger
from game.models import Board


class RandomAgent(BaseAgent):
    def __init__(self) -> None:
        self._untried_cells: list[tuple[int, int]] = [
            (r, c) for r in range(Board.board_size) for c in range(Board.board_size)
        ]
        self._rng = random.Random()
        GameLogger.info("Initialized RandomAgent")

    def select_move(self, obs: dict) -> str:
        if not self._untried_cells:
            raise RuntimeError("No untried cells remain")
        cell = self._rng.choice(self._untried_cells)
        self._untried_cells.remove(cell)
        formatted_cell = format_coordinate(cell[0], cell[1])
        return formatted_cell

    def reset(self) -> None:
        self._untried_cells = [
            (r, c) for r in range(Board.board_size) for c in range(Board.board_size)
        ]
        GameLogger.info("RandomAgent state reset")
