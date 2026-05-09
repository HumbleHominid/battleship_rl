---
type: community
cohesion: 0.10
members: 22
---

# Coordinate & Game Core

**Cohesion:** 0.10 - loosely connected
**Members:** 22 nodes

## Members
- [[Format zero-indexed (row, col) to 'A1'-'J10'.]] - rationale - game/coordinate_methods.py
- [[Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input.]] - rationale - game/coordinate_methods.py
- [[agent_score()]] - code - game/game_engine.py
- [[close()]] - code - game/logger.py
- [[coordinate_methods.py]] - code - game/coordinate_methods.py
- [[debug()]] - code - game/logger.py
- [[directions.py]] - code - game/directions.py
- [[error()]] - code - game/logger.py
- [[format_coordinate()]] - code - game/coordinate_methods.py
- [[game_board.py]] - code - game/game_board.py
- [[game_engine.py]] - code - game/game_engine.py
- [[game_over()]] - code - game/game_engine.py
- [[info()]] - code - game/logger.py
- [[logger.py]] - code - game/logger.py
- [[parse_coordinate()]] - code - game/coordinate_methods.py
- [[player_connected()]] - code - game/websocket.py
- [[player_score()]] - code - game/game_engine.py
- [[setup()]] - code - game/logger.py
- [[turn()]] - code - game/game_engine.py
- [[warn()]] - code - game/logger.py
- [[websocket.py]] - code - game/websocket.py
- [[winner()]] - code - game/game_engine.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Coordinate_&_Game_Core
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Fleet Placement]]
- 3 edges to [[_COMMUNITY_Game Board & Actions]]
- 1 edge to [[_COMMUNITY_Game Engine Loop]]

## Top bridge nodes
- [[logger.py]] - degree 11, connects to 2 communities
- [[game_board.py]] - degree 6, connects to 2 communities
- [[game_engine.py]] - degree 10, connects to 1 community
- [[websocket.py]] - degree 4, connects to 1 community
- [[directions.py]] - degree 2, connects to 1 community