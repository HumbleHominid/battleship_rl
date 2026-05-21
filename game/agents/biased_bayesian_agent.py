import random
from typing import Optional

from game.agents.bayesian_agent import BayesianAgent
from game.coordinate_methods import format_coordinate
from game.game_board import GameBoard
from game.game_logger import GameLogger
from game.models import Board, ShipType


class BiasedBayesianAgent(BayesianAgent):
    """Bayesian probability density agent biased toward human placements.

    Maintains a 10x10 density matrix compiled from simulated human placements,
    and multiplies the exact logical Bayesian placement counts by this prior.
    """

    def __init__(
        self,
        deterministic_selection: bool = False,
        alpha: float = 10.0,
        num_simulations: int = 2000,
    ) -> None:
        super().__init__(deterministic_selection=deterministic_selection)

        # Precompute the empirical cognitive human density prior
        self._density_grid = [
            [0.0] * Board.board_size for _ in range(Board.board_size)
        ]

        GameLogger.info(
            "Compiling empirical cognitive human density prior (2000 simulations)..."
        )
        # Run simulations using a dummy GameBoard to capture placement density
        for _ in range(num_simulations):
            board = GameBoard()
            board.place_fleet("cognitive_human")
            for r in range(Board.board_size):
                for c in range(Board.board_size):
                    ship_type, _ = board.board.get_cell(r, c)
                    if ship_type != ShipType.NONE:
                        self._density_grid[r][c] += 1.0

        # Apply smoothing (alpha) and normalize
        total_density = 0.0
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                self._density_grid[r][c] += alpha
                total_density += self._density_grid[r][c]

        # Divide each cell by the average cell density to keep values around 1.0 on average,
        # preserving the general range of counts.
        avg_density = total_density / (Board.board_size * Board.board_size)
        for r in range(Board.board_size):
            for c in range(Board.board_size):
                self._density_grid[r][c] /= avg_density

        GameLogger.info(
            "Initialized BiasedBayesianAgent with smoothed human placement prior"
        )

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

        # Compute biased scores for each unshot cell
        scores = {}
        for r, c in unshot_cells:
            scores[(r, c)] = self._grid[r][c] * self._density_grid[r][c]

        best_score = max(scores.values())
        if best_score == 0:
            GameLogger.debug("All placements exhausted, falling back to random")
            return format_coordinate(*self._rng.choice(unshot_cells))

        # Use a small tolerance for floating point comparison to group equal best scores
        candidates = sorted(
            (r, c) for r, c in unshot_cells if abs(scores[(r, c)] - best_score) < 1e-9
        )
        chosen = (
            candidates[0]
            if self._deterministic_selection
            else self._rng.choice(candidates)
        )

        GameLogger.debug(
            "Selected %s with biased probability score %.3f (raw count %d)",
            format_coordinate(*chosen),
            best_score,
            self._grid[chosen[0]][chosen[1]],
        )
        return format_coordinate(*chosen)
