import random
from typing import Optional

from game.agents.base_agent import BaseAgent
from game.coordinate_methods import format_coordinate, parse_coordinate
from game.game_logger import GameLogger
from game.models import Board, ShipType


class HuntAgent(BaseAgent):
    """Hunt-and-target agent.

    Search phase: shoots only checkerboard cells (row+col) % 2 == 0, guaranteeing
    any ship of size >= 2 is found in at most 50 shots.

    Hunt phase: on a confirmed hit, queues all four cardinal neighbors at low priority.
    Once two aligned hits reveal orientation, locks to that axis and prepends the two
    axis-aligned end cells at high priority (front of queue). Subsequent axis hits
    also prepend their extensions, keeping current-ship targeting ahead of residual
    queue items from other ships hit incidentally during the same run.

    On each select_move, the board is scanned for unresolved hits so that if the
    queue was exhausted without fully resolving a ship (e.g. due to prior-shot hit
    cells being silently skipped), those cells' neighbors are re-queued before
    falling through to search mode.

    On sink: clears active hit tracking but keeps the residual queue for any other
    ships hit incidentally.
    """

    def __init__(self) -> None:
        self._untried: set[tuple[int, int]] = set()
        self._search_cells: list[tuple[int, int]] = []
        self._queue: list[tuple[int, int]] = []
        self._active_hits: list[tuple[int, int]] = []
        self._sunk_ship_types: set[ShipType] = set()
        self._axis: Optional[tuple[int, int]] = None
        self._rng = random.Random()
        self._reset_state()
        GameLogger.info("Initialized HuntAgent")

    def _reset_state(self) -> None:
        self._untried = {
            (r, c) for r in range(Board.board_size) for c in range(Board.board_size)
        }
        checkerboard = [
            (r, c)
            for r in range(Board.board_size)
            for c in range(Board.board_size)
            if (r + c) % 2 == 0
        ]
        self._rng.shuffle(checkerboard)
        self._search_cells = checkerboard
        self._queue = []
        self._active_hits = []
        self._sunk_ship_types = set()
        self._axis = None

    def reset(self) -> None:
        self._reset_state()
        GameLogger.info("HuntAgent state reset")

    def _enqueue_back(self, cell: tuple[int, int]) -> None:
        if cell in self._untried and cell not in self._queue:
            self._queue.append(cell)

    def _enqueue_front(self, cell: tuple[int, int]) -> None:
        if cell in self._untried and cell not in self._queue:
            self._queue.insert(0, cell)

    def _cardinal_neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        return [
            (nr, nc)
            for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            if 0 <= nr < Board.board_size and 0 <= nc < Board.board_size
        ]

    def _prepend_axis_ends(self) -> None:
        """Prepend the two axis-aligned end cells to the front of the queue."""
        dr, dc = self._axis  # type: ignore[misc]
        if dr == 1:  # vertical
            rows = sorted(r for r, _ in self._active_hits)
            col = self._active_hits[0][1]
            ends = [(rows[0] - 1, col), (rows[-1] + 1, col)]
        else:  # horizontal
            cols = sorted(c for _, c in self._active_hits)
            row = self._active_hits[0][0]
            ends = [(row, cols[0] - 1), (row, cols[-1] + 1)]
        # Insert in reverse so the "forward" end lands at index 0
        for r, c in reversed(ends):
            if 0 <= r < Board.board_size and 0 <= c < Board.board_size:
                self._enqueue_front((r, c))

    def _queue_unresolved_from_board(self, board: list[list[str]]) -> None:
        """Scan board for unresolved hit cells and enqueue their unshot neighbors."""
        sunk_names = {st.name for st in self._sunk_ship_types}
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                ship_name, state = board[r][c].split(":")
                if state == "HIT" and ship_name not in sunk_names:
                    for neighbor in self._cardinal_neighbors(r, c):
                        self._enqueue_back(neighbor)

    def receive_result(
        self, coordinate: str, result: str, ship_sunk: Optional[str]
    ) -> None:
        row, col = parse_coordinate(coordinate)
        self._untried.discard((row, col))

        if result == "HIT":
            self._active_hits.append((row, col))

            if self._axis is None:
                if len(self._active_hits) >= 2:
                    r1, c1 = self._active_hits[-2]
                    r2, c2 = self._active_hits[-1]
                    if r1 == r2:
                        self._axis = (0, 1)  # horizontal
                    elif c1 == c2:
                        self._axis = (1, 0)  # vertical

                    if self._axis is not None:
                        # Lock acquired: push axis ends to front, keep other queue items
                        self._prepend_axis_ends()
                    else:
                        # Two misaligned hits — different ships; queue neighbors normally
                        for cell in self._cardinal_neighbors(row, col):
                            self._enqueue_back(cell)
                else:
                    # First hit — queue all four neighbors at low priority
                    for cell in self._cardinal_neighbors(row, col):
                        self._enqueue_back(cell)
            else:
                # Axis locked — extend in both directions at high priority
                dr, dc = self._axis
                for nr, nc in [(row - dr, col - dc), (row + dr, col + dc)]:
                    if 0 <= nr < Board.board_size and 0 <= nc < Board.board_size:
                        self._enqueue_front((nr, nc))

        if ship_sunk:
            self._sunk_ship_types.add(ShipType[ship_sunk.upper()])
            self._active_hits.clear()
            self._axis = None
            self._queue = [cell for cell in self._queue if cell in self._untried]

    def select_move(self, obs: dict) -> str:
        board = obs["enemy_board"]

        # Hunt mode: drain the queue front-to-back
        while self._queue:
            cell = self._queue.pop(0)
            if cell in self._untried:
                GameLogger.debug("HuntAgent hunt → %s", format_coordinate(*cell))
                return format_coordinate(*cell)

        # Queue exhausted: scan board for any unresolved hits we've lost track of
        # (happens when previously-shot HIT cells are silently skipped from the queue)
        self._queue_unresolved_from_board(board)
        while self._queue:
            cell = self._queue.pop(0)
            if cell in self._untried:
                GameLogger.debug(
                    "HuntAgent hunt (recovered) → %s", format_coordinate(*cell)
                )
                return format_coordinate(*cell)

        # Search mode: next checkerboard cell
        while self._search_cells:
            cell = self._search_cells.pop()
            if cell in self._untried:
                GameLogger.debug("HuntAgent search → %s", format_coordinate(*cell))
                return format_coordinate(*cell)

        raise RuntimeError("No cells remain")
