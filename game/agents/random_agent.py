import logging
import random

from game.agents.base_agent import BaseAgent
from game.coordinate_methods import format_coordinate
from game.models import Board

log = logging.getLogger(__name__)


class RandomAgent(BaseAgent):
    def __init__(self) -> None:
        self.reset()

    def select_move(self, obs: dict) -> str:
        if not self._untried_cells:
            raise RuntimeError("No untried cells remain")
        cell = random.choice(self._untried_cells)
        self._untried_cells.remove(cell)
        return format_coordinate(*cell)

    def reset(self) -> None:
        self._untried_cells: list[tuple[int, int]] = [
            (r, c) for r in range(Board.board_size) for c in range(Board.board_size)
        ]
        log.info("RandomAgent state reset")
