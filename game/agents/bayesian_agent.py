import random
from typing import Optional

from game.agents.base_agent import BaseAgent
from game.coordinate_methods import format_coordinate, parse_coordinate
from game.game_logger import GameLogger
from game.models import Board, Ship, ShipType, get_ship_size


class BayesianAgent(BaseAgent):
    """Bayesian probability density agent.

    Enumerates all valid ship placements once, then permanently eliminates
    placements inconsistent with observed misses/sinks. The probability grid
    is recomputed from remaining valid placements after each observation.

    Switches to target mode when there are unresolved hit cells: only placements
    covering at least one hit cell are counted, focusing fire on the damaged ship.
    """

    def __init__(self, deterministic_selection: bool = False) -> None:
        self._valid_placements: dict[ShipType, list[frozenset[tuple[int, int]]]] = {}
        self._grid: list[list[int]] = [
            [0] * Board.board_size for _ in range(Board.board_size)
        ]
        self._unresolved_hits: set[tuple[int, int]] = set()
        self._sunk_ship_types: set[ShipType] = set()
        self._initialized: bool = False
        self._rng = random.Random()
        self._deterministic_selection = deterministic_selection
        GameLogger.info("Initialized BayesianAgent")

    def reset(self) -> None:
        self._valid_placements = {}
        self._grid = [[0] * Board.board_size for _ in range(Board.board_size)]
        self._unresolved_hits = set()
        self._sunk_ship_types = set()
        self._initialized = False
        GameLogger.debug("ProbabilityAgent state reset")

    def init(self) -> None:
        """Explicitly initialize placements and compute the starting grid."""
        self._initialize_placements()
        self._recompute_grid()

    def _initialize_placements(self) -> None:
        for ship_type in Ship.get_fleet():
            size = get_ship_size(ship_type)
            placements: list[frozenset[tuple[int, int]]] = []
            for dr, dc in [(0, 1), (1, 0)]:
                for r in range(Board.board_size):
                    for c in range(Board.board_size):
                        cells = frozenset((r + dr * i, c + dc * i) for i in range(size))
                        if all(
                            0 <= cr < Board.board_size and 0 <= cc < Board.board_size
                            for cr, cc in cells
                        ):
                            placements.append(cells)
            self._valid_placements[ship_type] = placements
        self._initialized = True
        total = sum(len(p) for p in self._valid_placements.values())
        GameLogger.debug(
            "Initialized %d total placements across %d ships",
            total,
            len(self._valid_placements),
        )

    def _recompute_grid(self) -> None:
        grid = [[0] * Board.board_size for _ in range(Board.board_size)]
        target_mode = len(self._unresolved_hits) > 0
        for placements in self._valid_placements.values():
            for placement in placements:
                if target_mode and not (placement & self._unresolved_hits):
                    continue
                for r, c in placement:
                    grid[r][c] += 1
        self._grid = grid

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        if not self._initialized:
            return

        row, col = parse_coordinate(coordinate)

        if result == "MISS":
            cell = (row, col)
            for ship_type in self._valid_placements:
                self._valid_placements[ship_type] = [
                    p for p in self._valid_placements[ship_type] if cell not in p
                ]
            self._recompute_grid()
        elif result == "HIT":
            self._unresolved_hits.add((row, col))
            self._recompute_grid()

        if ship_sunk:
            ship_type = ShipType[ship_sunk.upper()]
            self._sunk_ship_types.add(ship_type)
            self._valid_placements.pop(ship_type, None)
            self._recompute_grid()

    def resolve_sunk_hits(self, obs: dict) -> None:
        """Remove hit cells of sunk ships from _unresolved_hits and recompute grid."""
        if not self._initialized:
            return
        board = obs["enemy_board"]
        sunk_names = {st.name for st in self._sunk_ship_types}
        hits_changed = False
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                ship_name, state = board[r][c].split(":")
                if state == "HIT" and ship_name in sunk_names:
                    if (r, c) in self._unresolved_hits:
                        self._unresolved_hits.discard((r, c))
                        hits_changed = True
        if hits_changed:
            self._recompute_grid()

    def select_move(self, obs: dict) -> str:
        if not self._initialized:
            self._initialize_placements()
            self._recompute_grid()

        board = obs["enemy_board"]
        sunk_names = {st.name for st in self._sunk_ship_types}
        unshot_cells: list[tuple[int, int]] = []
        hits_changed = False

        for r in range(Board.board_size):
            for c in range(Board.board_size):
                ship_name, state = board[r][c].split(":")
                if state == "EMPTY":
                    unshot_cells.append((r, c))
                elif state == "HIT" and ship_name in sunk_names:
                    if (r, c) in self._unresolved_hits:
                        self._unresolved_hits.discard((r, c))
                        hits_changed = True

        if hits_changed:
            self._recompute_grid()

        if not unshot_cells:
            raise RuntimeError("No unshot cells remain")

        best_count = max(self._grid[r][c] for r, c in unshot_cells)
        if best_count == 0:
            GameLogger.debug("All placements exhausted, falling back to random")
            return format_coordinate(*self._rng.choice(unshot_cells))

        candidates = sorted(
            (r, c) for r, c in unshot_cells if self._grid[r][c] == best_count
        )
        chosen = (
            candidates[0]
            if self._deterministic_selection
            else self._rng.choice(candidates)
        )
        GameLogger.debug(
            "Selected %s with probability count %d",
            format_coordinate(*chosen),
            best_count,
        )
        return format_coordinate(*chosen)
