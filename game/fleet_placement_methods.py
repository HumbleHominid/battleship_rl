import math
import random
from typing import Callable

from game.coordinate_methods import format_coordinate
from game.models import Board

from .directions import DIRECTIONS
from .game_logger import GameLogger
from .models import Ship
from .placement_protocol import PlacementTarget

PlacementMethod = Callable[[PlacementTarget], None]

_MAX_RETRIES = 1000
_SPREAD_CANDIDATES = 30
_SCORED_CANDIDATES = 30
_GAUSSIAN_N_HOTSPOTS = 3
_GAUSSIAN_SIGMA = 2.5
_CLUSTER_SIGMA = 1.5

_DIRECTIONS = list(DIRECTIONS.keys())
_CORNERS = [
    (0, 0),
    (0, Board.board_size - 1),
    (Board.board_size - 1, 0),
    (Board.board_size - 1, Board.board_size - 1),
]


def _edge_dist(r: int, c: int) -> float:
    return float(min(r, Board.board_size - 1 - r, c, Board.board_size - 1 - c))


def _corner_dist(r: int, c: int) -> float:
    return min(math.sqrt((r - cr) ** 2 + (c - cc) ** 2) for cr, cc in _CORNERS)


def _center_dist(r: int, c: int) -> float:
    return math.sqrt((r - 4.5) ** 2 + (c - 4.5) ** 2)


def _diag_dist(r: int, c: int) -> float:
    return abs(r - c) / math.sqrt(2)


def _best_scored_candidate(
    board: PlacementTarget,
    ship_type,
    score_fn: Callable[[int, int], float],
    lower_is_better: bool = True,
) -> tuple[int, int, str] | None:
    best: tuple[int, int, str] | None = None
    best_score = float("inf") if lower_is_better else float("-inf")
    for _ in range(_SCORED_CANDIDATES):
        row = random.randint(0, Board.board_size - 1)
        col = random.randint(0, Board.board_size - 1)
        direction = random.choice(_DIRECTIONS)
        valid, _ = board.can_place_ship(ship_type, row, col, direction)
        if not valid:
            continue
        score = score_fn(row, col)
        if (lower_is_better and score < best_score) or (
            not lower_is_better and score > best_score
        ):
            best_score = score
            best = (row, col, direction)
    return best


def _place_with_score(
    board: PlacementTarget,
    method_name: str,
    score_fn: Callable[[int, int], float],
    lower_is_better: bool = True,
) -> None:
    for ship_type in Ship.get_fleet():
        placed = False
        best = _best_scored_candidate(board, ship_type, score_fn, lower_is_better)
        if best is not None:
            board.place_ship(ship_type, *best)
            GameLogger.info(
                "Placed %s at %s facing %s",
                ship_type.name,
                format_coordinate(*best[:2]),
                best[2],
            )
            placed = True

        if not placed:
            for _ in range(_MAX_RETRIES):
                row = random.randint(0, Board.board_size - 1)
                col = random.randint(0, Board.board_size - 1)
                direction = random.choice(_DIRECTIONS)
                valid, _ = board.can_place_ship(ship_type, row, col, direction)
                if valid:
                    board.place_ship(ship_type, row, col, direction)
                    GameLogger.info(
                        "Placed %s at %s facing %s",
                        ship_type.name,
                        format_coordinate(row, col),
                        direction,
                    )
                    placed = True
                    break

        if not placed:
            err_str = _placement_error(method_name)
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def _placement_error(method: str) -> str:
    return f"Failed to place fleet using {method} after {_MAX_RETRIES} retries"


def place_fleet_random(board: PlacementTarget) -> None:
    for ship_type in Ship.get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            row = random.randint(0, Board.board_size - 1)
            col = random.randint(0, Board.board_size - 1)
            direction = random.choice(_DIRECTIONS)
            valid, _ = board.can_place_ship(ship_type, row, col, direction)
            if valid:
                board.place_ship(ship_type, row, col, direction)
                cell = format_coordinate(row, col)
                GameLogger.info(
                    "Placed %s at %s facing %s",
                    ship_type.name,
                    cell,
                    direction,
                )
                placed = True
                break
        if not placed:
            err_str = _placement_error("random")
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def place_fleet_gaussian(board: PlacementTarget) -> None:
    hotspots = [
        (
            random.randint(1, Board.board_size - 2),
            random.randint(1, Board.board_size - 2),
        )
        for _ in range(_GAUSSIAN_N_HOTSPOTS)
    ]
    for ship_type in Ship.get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            hr, hc = random.choice(hotspots)
            row = max(
                0, min(Board.board_size - 1, round(random.gauss(hr, _GAUSSIAN_SIGMA)))
            )
            col = max(
                0, min(Board.board_size - 1, round(random.gauss(hc, _GAUSSIAN_SIGMA)))
            )
            direction = random.choice(_DIRECTIONS)
            valid, _ = board.can_place_ship(ship_type, row, col, direction)
            if valid:
                board.place_ship(ship_type, row, col, direction)
                cell = format_coordinate(row, col)
                GameLogger.info(
                    "Placed %s at %s facing %s",
                    ship_type.name,
                    cell,
                    direction,
                )
                placed = True
                break
        if not placed:
            err_str = _placement_error("gaussian")
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def place_fleet_spread(board: PlacementTarget) -> None:
    for ship_type in Ship.get_fleet():
        placed = False
        occupied = board.get_placed_cells()

        if occupied:
            best: tuple[int, int, str] | None = None
            best_score = -1.0
            for _ in range(_SPREAD_CANDIDATES):
                row = random.randint(0, Board.board_size - 1)
                col = random.randint(0, Board.board_size - 1)
                direction = random.choice(_DIRECTIONS)
                valid, _ = board.can_place_ship(ship_type, row, col, direction)
                if not valid:
                    continue
                score = min(
                    math.sqrt((row - r) ** 2 + (col - c) ** 2) for r, c in occupied
                )
                if score > best_score:
                    best_score = score
                    best = (row, col, direction)
            if best is not None:
                board.place_ship(ship_type, *best)
                cell = format_coordinate(*best[:2])
                GameLogger.info(
                    "Placed %s at %s facing %s",
                    ship_type.name,
                    cell,
                    best[2],
                )
                placed = True

        if not placed:
            for _ in range(_MAX_RETRIES):
                row = random.randint(0, Board.board_size - 1)
                col = random.randint(0, Board.board_size - 1)
                direction = random.choice(_DIRECTIONS)
                valid, _ = board.can_place_ship(ship_type, row, col, direction)
                if valid:
                    board.place_ship(ship_type, row, col, direction)
                    cell = format_coordinate(row, col)
                    GameLogger.info(
                        "Placed %s at %s facing %s",
                        ship_type.name,
                        cell,
                        direction,
                    )
                    placed = True
                    break

        if not placed:
            err_str = _placement_error("spread")
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def place_fleet_edges(board: PlacementTarget) -> None:
    """Bias ships toward the board perimeter (minimise distance to nearest edge)."""
    _place_with_score(board, "edges", _edge_dist, lower_is_better=True)


def place_fleet_corners(board: PlacementTarget) -> None:
    """Bias ships toward the four corners (minimise distance to nearest corner)."""
    _place_with_score(board, "corners", _corner_dist, lower_is_better=True)


def place_fleet_clustered(board: PlacementTarget) -> None:
    """Pack all ships tightly around a single random hotspot (opposite of spread)."""
    hr, hc = random.randint(1, Board.board_size - 2), random.randint(
        1, Board.board_size - 2
    )
    for ship_type in Ship.get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            row = max(
                0, min(Board.board_size - 1, round(random.gauss(hr, _CLUSTER_SIGMA)))
            )
            col = max(
                0, min(Board.board_size - 1, round(random.gauss(hc, _CLUSTER_SIGMA)))
            )
            direction = random.choice(_DIRECTIONS)
            valid, _ = board.can_place_ship(ship_type, row, col, direction)
            if valid:
                board.place_ship(ship_type, row, col, direction)
                GameLogger.info(
                    "Placed %s at %s facing %s",
                    ship_type.name,
                    format_coordinate(row, col),
                    direction,
                )
                placed = True
                break
        if not placed:
            err_str = _placement_error("clustered")
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def place_fleet_quadrant(board: PlacementTarget) -> None:
    """Confine the entire fleet to one randomly chosen quadrant."""
    row_range, col_range = random.choice(
        [
            ((0, Board.board_size // 2 - 1), (0, Board.board_size // 2 - 1)),
            (
                (0, Board.board_size // 2 - 1),
                (Board.board_size // 2, Board.board_size - 1),
            ),
            (
                (Board.board_size // 2, Board.board_size - 1),
                (0, Board.board_size // 2 - 1),
            ),
            (
                (Board.board_size // 2, Board.board_size - 1),
                (Board.board_size // 2, Board.board_size - 1),
            ),
        ]
    )
    for ship_type in Ship.get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            row = random.randint(*row_range)
            col = random.randint(*col_range)
            direction = random.choice(_DIRECTIONS)
            valid, _ = board.can_place_ship(ship_type, row, col, direction)
            if valid:
                board.place_ship(ship_type, row, col, direction)
                GameLogger.info(
                    "Placed %s at %s facing %s",
                    ship_type.name,
                    format_coordinate(row, col),
                    direction,
                )
                placed = True
                break
        if not placed:
            err_str = _placement_error("quadrant")
            GameLogger.error(err_str)
            raise RuntimeError(err_str)


def place_fleet_dense_center(board: PlacementTarget) -> None:
    """Bias ships toward the centre (minimise distance to board centre at 4.5, 4.5)."""
    _place_with_score(board, "dense_center", _center_dist, lower_is_better=True)


def place_fleet_diagonal(board: PlacementTarget) -> None:
    """Bias ships toward the main diagonal (where row == col)."""
    _place_with_score(board, "diagonal", _diag_dist, lower_is_better=True)


# Relative weights control how often each algorithm is selected.
# Edit the first element of each tuple to tune the distribution.
PLACEMENT_METHODS: dict[str, tuple[int, PlacementMethod]] = {
    "random": (1, place_fleet_random),
    "gaussian": (1, place_fleet_gaussian),
    "spread": (1, place_fleet_spread),
    "edges": (1, place_fleet_edges),
    "corners": (1, place_fleet_corners),
    "clustered": (1, place_fleet_clustered),
    "quadrant": (1, place_fleet_quadrant),
    "dense_center": (1, place_fleet_dense_center),
    "diagonal": (1, place_fleet_diagonal),
}
