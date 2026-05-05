from .cell_state import CellState
from .ship import Ship
from .ship_type import ShipType


class Board:
    board_size = 10

    def __init__(self, board_size: int = 10) -> None:
        # board[row][col] = (ShipType, CellState)
        Board.board_size = board_size

        self.board: list[list[tuple[ShipType, CellState]]] = [
            [(ShipType.NONE, CellState.EMPTY) for _ in range(Board.board_size)]
            for _ in range(Board.board_size)
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
