from game.models import Board

ROW_LABELS = "ABCDEFGHIJ"  # index 0='A' ... 9='J'


def parse_coordinate(coord: str) -> tuple[int, int]:
    """Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input."""
    coord = coord.strip().upper()
    valid_labels = ROW_LABELS[: Board.board_size]
    if len(coord) < 2:
        raise ValueError(f"Invalid coordinate: '{coord}'")
    row_char = coord[0]
    col_str = coord[1:]
    if row_char not in valid_labels:
        raise ValueError(f"Row '{row_char}' out of range A-{ROW_LABELS[-1]}")
    try:
        col = int(col_str)
    except ValueError:
        raise ValueError(f"Column '{col_str}' is not a number")
    if col < 1 or col > Board.board_size:
        raise ValueError(f"Column {col} out of range 1-{Board.board_size}")
    return ROW_LABELS.index(row_char), col - 1


def format_coordinate(row: int, col: int) -> str:
    """Format zero-indexed (row, col) to 'A1'-'J10'."""
    return f"{ROW_LABELS[row]}{col + 1}"
