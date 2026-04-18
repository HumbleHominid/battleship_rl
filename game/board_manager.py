import random
from typing import Optional

from .directions import DIRECTIONS
from .models import CellState, GameBoard, Ship, ShipType, get_fleet, get_ship_size

ROW_LABELS = "ABCDEFGHIJ"  # index 0='A' ... 9='J'

_MAX_PLACEMENT_RETRIES = 1000


class BoardManager:
    def __init__(self, board: GameBoard) -> None:
        self.board = board

    # ------------------------------------------------------------------
    # Coordinate parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_coordinate(coord: str) -> tuple[int, int]:
        """Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input."""
        coord = coord.strip().upper()
        if len(coord) < 2:
            raise ValueError(f"Invalid coordinate: '{coord}'")
        row_char = coord[0]
        col_str = coord[1:]
        if row_char not in ROW_LABELS:
            raise ValueError(f"Row '{row_char}' out of range A-J")
        try:
            col = int(col_str)
        except ValueError:
            raise ValueError(f"Column '{col_str}' is not a number")
        if col < 1 or col > 10:
            raise ValueError(f"Column {col} out of range 1-10")
        return ROW_LABELS.index(row_char), col - 1

    @staticmethod
    def format_coordinate(row: int, col: int) -> str:
        """Format zero-indexed (row, col) to 'A1'-'J10'."""
        return f"{ROW_LABELS[row]}{col + 1}"

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def _ship_cells(
        self, ship_type: ShipType, row: int, col: int, direction: str
    ) -> list[tuple[int, int]]:
        """Compute the list of (row, col) cells a ship would occupy."""
        direction = direction.lower()
        if direction not in DIRECTIONS:
            raise ValueError(
                f"Direction '{direction}' must be one of {list(DIRECTIONS)}"
            )
        dr, dc = DIRECTIONS[direction]
        size = get_ship_size(ship_type)
        return [(row + dr * i, col + dc * i) for i in range(size)]

    def can_place_ship(
        self, ship_type: ShipType, row: int, col: int, direction: str
    ) -> tuple[bool, str]:
        """
        Return (True, '') if the placement is valid.
        Return (False, reason) if out of bounds or overlapping an existing ship.
        """
        try:
            cells = self._ship_cells(ship_type, row, col, direction)
        except ValueError as e:
            return False, str(e)

        for r, c in cells:
            if not (0 <= r <= 9 and 0 <= c <= 9):
                return False, (
                    f"Ship extends out of bounds at "
                    f"{BoardManager.format_coordinate(max(0, min(r, 9)), max(0, min(c, 9)))}"
                )
            if self.board.get_cell(r, c)[0] is not ShipType.NONE:
                return False, (
                    f"Cell {BoardManager.format_coordinate(r, c)} is already occupied"
                )
        return True, ""

    def place_ship(
        self, ship_type: ShipType, row: int, col: int, direction: str
    ) -> Ship:
        """
        Place a ship on the board. Raises ValueError if placement is invalid.
        Returns the placed Ship.
        """
        valid, reason = self.can_place_ship(ship_type, row, col, direction)
        if not valid:
            raise ValueError(f"Cannot place {ship_type.name}: {reason}")

        cells = self._ship_cells(ship_type, row, col, direction)
        ship = Ship(ship_type=ship_type, cells=cells)
        for r, c in cells:
            self.board.set_cell(r, c, ship_type, CellState.EMPTY)
        self.board.ships.append(ship)
        return ship

    def place_ship_from_str(
        self, ship_type: ShipType, coord: str, direction: str
    ) -> Ship:
        """Convenience wrapper: place_ship_from_str(ShipType.CARRIER, 'A1', 'right')."""
        row, col = self.parse_coordinate(coord)
        return self.place_ship(ship_type, row, col, direction)

    def place_fleet_randomly(self) -> None:
        """Randomly place all ships. Retries on collision."""
        directions = list(DIRECTIONS.keys())
        for ship_type in get_fleet():
            placed = False
            for _ in range(_MAX_PLACEMENT_RETRIES):
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                direction = random.choice(directions)
                valid, _ = self.can_place_ship(ship_type, row, col, direction)
                if valid:
                    self.place_ship(ship_type, row, col, direction)
                    placed = True
                    break
            if not placed:
                raise RuntimeError(
                    f"Failed to place {ship_type.name} after {_MAX_PLACEMENT_RETRIES} retries"
                )

    # ------------------------------------------------------------------
    # Hit detection
    # ------------------------------------------------------------------

    def find_ship_at(self, row: int, col: int) -> Optional[Ship]:
        """Return the Ship occupying this cell, or None."""
        for ship in self.board.ships:
            if (row, col) in ship.cells:
                return ship
        return None

    def receive_shot(self, row: int, col: int) -> tuple[CellState, Optional[Ship]]:
        """
        Process an incoming shot.
        Returns (CellState.HIT, Ship) on hit, (CellState.MISS, None) on miss.
        Raises ValueError if the cell has already been shot.
        """
        ship_type, current_state = self.board.get_cell(row, col)
        if current_state in (CellState.HIT, CellState.MISS):
            raise ValueError(
                f"Cell {self.format_coordinate(row, col)} has already been shot"
            )

        if ship_type is not ShipType.NONE:
            ship = self.find_ship_at(row, col)
            self.board.set_cell(row, col, ship_type, CellState.HIT)
            if ship:
                ship.register_hit()
            return CellState.HIT, ship
        else:
            self.board.set_cell(row, col, ShipType.NONE, CellState.MISS)
            return CellState.MISS, None

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk for ship in self.board.ships)

    def ships_sunk_count(self) -> int:
        return sum(1 for ship in self.board.ships if ship.is_sunk)

    def cells_hit_count(self) -> int:
        return sum(
            1 for row in self.board.board for _, state in row if state is CellState.HIT
        )

    def get_unhit_cells(self) -> list[tuple[int, int]]:
        """Return all (row, col) pairs not yet shot (EMPTY or ship still there)."""
        return [
            (r, c)
            for r in range(10)
            for c in range(10)
            if self.board.get_cell(r, c)[1] is CellState.EMPTY
        ]

    def board_as_matrix(self, fog_of_war: bool = False) -> list[list[str]]:
        """
        Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.
        If fog_of_war=True, ship types are hidden as NONE unless the cell is HIT.
        """
        result = []
        for r in range(10):
            row_data = []
            for c in range(10):
                ship_type, state = self.board.get_cell(r, c)
                if fog_of_war and state is not CellState.HIT:
                    ship_type = ShipType.NONE
                row_data.append(f"{ship_type.name}:{state.name}")
            result.append(row_data)
        return result

    # ------------------------------------------------------------------
    # Terminal display
    # ------------------------------------------------------------------

    def _cell_symbol(self, ship_type: ShipType, state: CellState, fog: bool) -> str:
        if state is CellState.HIT:
            return "X"
        if state is CellState.MISS:
            return "o"
        # EMPTY
        if fog or ship_type is ShipType.NONE:
            return "."
        return ship_type.name[0]

    def display(self, fog_of_war: bool = False, label: str = "") -> None:
        """Print the board to stdout with row/col headers."""
        header = f"  {'  '.join(str(c) for c in range(1, 11))}"
        if label:
            print(f"\n{label}")
        print(header)
        for r in range(10):
            cells = []
            for c in range(10):
                ship_type, state = self.board.get_cell(r, c)
                cells.append(self._cell_symbol(ship_type, state, fog_of_war))
            print(f"{ROW_LABELS[r]} {' '.join(f'{sym:2}' for sym in cells)}")
        print()
