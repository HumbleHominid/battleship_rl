from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from game.game_board import GameBoard


class BaseAgent(ABC):
    @abstractmethod
    def select_move(self, obs: dict) -> str:
        """Return a coordinate string (e.g. 'B5') given an observation dict."""
        ...

    def place_fleet(self, board: "GameBoard") -> None:
        """Place this agent's fleet. Defaults to GameBoard.place_fleet()."""
        board.place_fleet()

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        """Called after each move. Hook for training feedback; no-op by default."""

    def reset(self) -> None:
        """Reset agent state for a new episode."""
