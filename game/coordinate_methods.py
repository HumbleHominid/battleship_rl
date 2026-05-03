ROW_LABELS = "ABCDEFGHIJ"  # index 0='A' ... 9='J'


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


def format_coordinate(row: int, col: int) -> str:
    """Format zero-indexed (row, col) to 'A1'-'J10'."""
    return f"{ROW_LABELS[row]}{col + 1}"
