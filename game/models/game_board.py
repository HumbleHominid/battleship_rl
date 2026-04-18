from .cell_state import CellState
from .ship import Ship
from .ship_type import ShipType


class GameBoard:
    def __init__(self) -> None:
        # board[row][col] = (ShipType, CellState)
        self.board: list[list[tuple[ShipType, CellState]]] = [
            [(ShipType.NONE, CellState.EMPTY) for _ in range(10)] for _ in range(10)
        ]
        self.ships: list[Ship] = []

    def get_cell(self, row: int, col: int) -> tuple[ShipType, CellState]:
        return self.board[row][col]

    def set_cell(
        self, row: int, col: int, ship_type: ShipType, state: CellState
    ) -> None:
        self.board[row][col] = (ship_type, state)

    def reset(self) -> None:
        self.__init__()
