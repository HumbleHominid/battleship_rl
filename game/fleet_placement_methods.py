import math
import random
from typing import Callable

from game.coordinate_methods import format_coordinate

from .directions import DIRECTIONS
from .logger import GameLogger
from .models import get_fleet
from .placement_protocol import PlacementTarget

PlacementMethod = Callable[[PlacementTarget], None]

_MAX_RETRIES = 1000
_SPREAD_CANDIDATES = 30
_GAUSSIAN_N_HOTSPOTS = 3
_GAUSSIAN_SIGMA = 2.5

_DIRECTIONS = list(DIRECTIONS.keys())


def _placement_error(method: str) -> str:
    return f"Failed to place fleet using {method} after {_MAX_RETRIES} retries"


def place_fleet_random(board: PlacementTarget) -> None:
    for ship_type in get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            row = random.randint(0, 9)
            col = random.randint(0, 9)
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
        (random.randint(1, 8), random.randint(1, 8))
        for _ in range(_GAUSSIAN_N_HOTSPOTS)
    ]
    for ship_type in get_fleet():
        placed = False
        for _ in range(_MAX_RETRIES):
            hr, hc = random.choice(hotspots)
            row = max(0, min(9, round(random.gauss(hr, _GAUSSIAN_SIGMA))))
            col = max(0, min(9, round(random.gauss(hc, _GAUSSIAN_SIGMA))))
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
    for ship_type in get_fleet():
        placed = False
        occupied = board.get_placed_cells()

        if occupied:
            best: tuple[int, int, str] | None = None
            best_score = -1.0
            for _ in range(_SPREAD_CANDIDATES):
                row = random.randint(0, 9)
                col = random.randint(0, 9)
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
                row = random.randint(0, 9)
                col = random.randint(0, 9)
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


# Relative weights control how often each algorithm is selected.
# Edit the first element of each tuple to tune the distribution.
PLACEMENT_METHODS: list[tuple[int, PlacementMethod]] = [
    (1, place_fleet_random),
    (1, place_fleet_gaussian),
    (1, place_fleet_spread),
]
