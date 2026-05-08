---
source_file: "game/game_board.py"
type: "code"
community: "Game Board & Actions"
location: "L11"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Game_Board_&_Actions
---

# GameBoard

## Connections
- [[.__init__()_1]] - `method` [EXTRACTED]
- [[._cell_symbol()]] - `method` [EXTRACTED]
- [[._ship_cells()]] - `method` [EXTRACTED]
- [[.all_ships_sunk()]] - `method` [EXTRACTED]
- [[.board_as_matrix()]] - `method` [EXTRACTED]
- [[.can_place_ship()_1]] - `method` [EXTRACTED]
- [[.cells_hit_count()]] - `method` [EXTRACTED]
- [[.cells_targeted()]] - `method` [EXTRACTED]
- [[.display()]] - `method` [EXTRACTED]
- [[.find_ship_at()]] - `method` [EXTRACTED]
- [[.get_placed_cells()_1]] - `method` [EXTRACTED]
- [[.get_unhit_cells()]] - `method` [EXTRACTED]
- [[.place_fleet()]] - `method` [EXTRACTED]
- [[.place_ship()_1]] - `method` [EXTRACTED]
- [[.place_ship_from_str()]] - `method` [EXTRACTED]
- [[.receive_shot()]] - `method` [EXTRACTED]
- [[.ships_sunk_count()]] - `method` [EXTRACTED]
- [[BaseAgent_1]] - `uses` [INFERRED]
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[Called after each move. Hook for training feedback; no-op by default.]] - `uses` [INFERRED]
- [[Fast single-game Battleship environment for RL training.      Wraps GameBoard di]] - `uses` [INFERRED]
- [[GameEngine]] - `uses` [INFERRED]
- [[GameLogger]] - `uses` [INFERRED]
- [[Orchestrates a full game of Battleship.      The game-side agent always runs in-]] - `uses` [INFERRED]
- [[Place this agent's fleet. Defaults to GameBoard.place_fleet().]] - `uses` [INFERRED]
- [[Reset agent state for a new episode.]] - `uses` [INFERRED]
- [[Return a coordinate string (e.g. 'B5') given an observation dict.]] - `uses` [INFERRED]
- [[Return list of cell indices (0–99) that have not yet been shot.]] - `uses` [INFERRED]
- [[Take a shot at cell index `action` (row  10 + col).          Returns]] - `uses` [INFERRED]
- [[game_board.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Game_Board_&_Actions