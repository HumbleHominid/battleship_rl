---
type: community
cohesion: 0.06
members: 55
---

# Game Board & Actions

**Cohesion:** 0.06 - loosely connected
**Members:** 55 nodes

## Members
- [[.__init__()_1]] - code - game/game_board.py
- [[.__init__()_2]] - code - game/websocket.py
- [[._cell_symbol()]] - code - game/game_board.py
- [[._handle_observer()]] - code - game/websocket.py
- [[._handle_player()]] - code - game/websocket.py
- [[._handler()]] - code - game/websocket.py
- [[._ship_cells()]] - code - game/game_board.py
- [[.all_ships_sunk()]] - code - game/game_board.py
- [[.board_as_matrix()]] - code - game/game_board.py
- [[.broadcast_state()]] - code - game/websocket.py
- [[.can_place_ship()_1]] - code - game/game_board.py
- [[.cells_hit_count()]] - code - game/game_board.py
- [[.cells_targeted()]] - code - game/game_board.py
- [[.display()]] - code - game/game_board.py
- [[.find_ship_at()]] - code - game/game_board.py
- [[.get_placed_cells()_1]] - code - game/game_board.py
- [[.get_unhit_cells()]] - code - game/game_board.py
- [[.legal_actions()]] - code - training/battleship_env.py
- [[.place_fleet()]] - code - game/game_board.py
- [[.place_ship()_1]] - code - game/game_board.py
- [[.place_ship_from_str()]] - code - game/game_board.py
- [[.receive_shot()]] - code - game/game_board.py
- [[.send_to_player()]] - code - game/websocket.py
- [[.ships_sunk_count()]] - code - game/game_board.py
- [[.start()]] - code - game/websocket.py
- [[.stop()]] - code - game/websocket.py
- [[.wait_for_player_move()]] - code - game/websocket.py
- [[.wait_for_player_placement()]] - code - game/websocket.py
- [[Await the next move coordinate from the player's move queue.]] - rationale - game/websocket.py
- [[Await the next ship placement message from the player's placement queue.]] - rationale - game/websocket.py
- [[Compute the list of (row, col) cells a ship would occupy.]] - rationale - game/game_board.py
- [[Convenience wrapper place_ship_from_str(ShipType.CARRIER, 'A1', 'right').]] - rationale - game/game_board.py
- [[Embedded WebSocket server that       - Broadcasts game state to all connected o]] - rationale - game/websocket.py
- [[Entry point for each new connection. Reads role, routes accordingly.]] - rationale - game/websocket.py
- [[GameBoard]] - code - game/game_board.py
- [[GameLogger]] - code - game/logger.py
- [[GameWebSocketServer]] - code - game/websocket.py
- [[Launch the WebSocket server and keep it alive until this coroutine is cancelled.]] - rationale - game/websocket.py
- [[Orchestrates a full game of Battleship.      The game-side agent always runs in-]] - rationale - game/game_engine.py
- [[Place a ship on the board. Raises ValueError if placement is invalid.         Re]] - rationale - game/game_board.py
- [[Place the full fleet using a weighted-random placement algorithm.          Algor]] - rationale - game/game_board.py
- [[Print the board to stdout with rowcol headers.]] - rationale - game/game_board.py
- [[Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta]] - rationale - game/game_board.py
- [[Receive move and placement commands from the player and enqueue them.]] - rationale - game/websocket.py
- [[Register an observer and hold its connection open until disconnect.]] - rationale - game/websocket.py
- [[Return (True, '') if the placement is valid.         Return (False, reason) if o]] - rationale - game/game_board.py
- [[Return a coordinate string (e.g. 'B5') given an observation dict.]] - rationale - game/agents/base_agent.py
- [[Return all (row, col) pairs not yet shot (EMPTY or ship still there).]] - rationale - game/game_board.py
- [[Return list of cell indices (0–99) that have not yet been shot.]] - rationale - training/battleship_env.py
- [[Return the Ship occupying this cell, or None.]] - rationale - game/game_board.py
- [[Send a JSON message to the connected player. No-op if none connected.]] - rationale - game/websocket.py
- [[Send close frames to all connected clients.]] - rationale - game/websocket.py
- [[Serialize board to a 10x10 list of 'SHIPTYPECELLSTATE' strings.         If fog_]] - rationale - game/game_board.py
- [[Serialize state_dict to JSON and send to all connected observers.]] - rationale - game/websocket.py
- [[Statically accessible logger. Call GameLogger.info()  .warn()  .error()  .deb]] - rationale - game/logger.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Game_Board_&_Actions
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Agent Interface]]
- 6 edges to [[_COMMUNITY_Fleet Placement]]
- 5 edges to [[_COMMUNITY_Training Environment]]
- 4 edges to [[_COMMUNITY_Game Engine Loop]]
- 3 edges to [[_COMMUNITY_Coordinate & Game Core]]
- 1 edge to [[_COMMUNITY_Agent Implementations]]
- 1 edge to [[_COMMUNITY_Game State Models]]

## Top bridge nodes
- [[GameLogger]] - degree 40, connects to 7 communities
- [[GameBoard]] - degree 30, connects to 4 communities
- [[GameWebSocketServer]] - degree 15, connects to 2 communities
- [[Orchestrates a full game of Battleship.      The game-side agent always runs in-]] - degree 5, connects to 2 communities
- [[.legal_actions()]] - degree 2, connects to 1 community