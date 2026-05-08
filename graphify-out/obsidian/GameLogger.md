---
source_file: "game/logger.py"
type: "code"
community: "Game Board & Actions"
location: "L11"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Game_Board_&_Actions
---

# GameLogger

## Connections
- [[Await the next move coordinate from the player's move queue.]] - `uses` [INFERRED]
- [[Await the next ship placement message from the player's placement queue.]] - `uses` [INFERRED]
- [[Bayesian probability density agent.      Enumerates all valid ship placements on]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[Bias ships toward the board perimeter (minimise distance to nearest edge).]] - `uses` [INFERRED]
- [[Bias ships toward the centre (minimise distance to board centre at 4.5, 4.5).]] - `uses` [INFERRED]
- [[Bias ships toward the four corners (minimise distance to nearest corner).]] - `uses` [INFERRED]
- [[Bias ships toward the main diagonal (where row == col).]] - `uses` [INFERRED]
- [[Board]] - `uses` [INFERRED]
- [[Compute the list of (row, col) cells a ship would occupy.]] - `uses` [INFERRED]
- [[Confine the entire fleet to one randomly chosen quadrant.]] - `uses` [INFERRED]
- [[Convenience wrapper place_ship_from_str(ShipType.CARRIER, 'A1', 'right').]] - `uses` [INFERRED]
- [[Embedded WebSocket server that       - Broadcasts game state to all connected o]] - `uses` [INFERRED]
- [[Entry point for each new connection. Reads role, routes accordingly.]] - `uses` [INFERRED]
- [[GameBoard]] - `uses` [INFERRED]
- [[GameEngine]] - `uses` [INFERRED]
- [[GameWebSocketServer]] - `uses` [INFERRED]
- [[Hunt-and-target agent.      Search phase shoots only checkerboard cells (row+co]] - `uses` [INFERRED]
- [[HuntAgent]] - `uses` [INFERRED]
- [[Launch the WebSocket server and keep it alive until this coroutine is cancelled.]] - `uses` [INFERRED]
- [[Orchestrates a full game of Battleship.      The game-side agent always runs in-]] - `uses` [INFERRED]
- [[Pack all ships tightly around a single random hotspot (opposite of spread).]] - `uses` [INFERRED]
- [[Place a ship on the board. Raises ValueError if placement is invalid.         Re]] - `uses` [INFERRED]
- [[Place the full fleet using a weighted-random placement algorithm.          Algor]] - `uses` [INFERRED]
- [[Prepend the two axis-aligned end cells to the front of the queue.]] - `uses` [INFERRED]
- [[Print the board to stdout with rowcol headers.]] - `uses` [INFERRED]
- [[Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta]] - `uses` [INFERRED]
- [[RandomAgent]] - `uses` [INFERRED]
- [[Receive move and placement commands from the player and enqueue them.]] - `uses` [INFERRED]
- [[Register an observer and hold its connection open until disconnect.]] - `uses` [INFERRED]
- [[Return (True, '') if the placement is valid.         Return (False, reason) if o]] - `uses` [INFERRED]
- [[Return all (row, col) pairs not yet shot (EMPTY or ship still there).]] - `uses` [INFERRED]
- [[Return the Ship occupying this cell, or None.]] - `uses` [INFERRED]
- [[Scan board for unresolved hit cells and enqueue their unshot neighbors.]] - `uses` [INFERRED]
- [[Send a JSON message to the connected player. No-op if none connected.]] - `uses` [INFERRED]
- [[Send close frames to all connected clients.]] - `uses` [INFERRED]
- [[Serialize board to a 10x10 list of 'SHIPTYPECELLSTATE' strings.         If fog_]] - `uses` [INFERRED]
- [[Serialize state_dict to JSON and send to all connected observers.]] - `uses` [INFERRED]
- [[Statically accessible logger. Call GameLogger.info()  .warn()  .error()  .deb]] - `rationale_for` [EXTRACTED]
- [[logger.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Game_Board_&_Actions