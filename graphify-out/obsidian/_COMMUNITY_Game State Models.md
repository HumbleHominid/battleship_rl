---
type: community
cohesion: 0.15
members: 23
---

# Game State Models

**Cohesion:** 0.15 - loosely connected
**Members:** 23 nodes

## Members
- [[NOTE ShipType enum values are priority IDs, not sizes.]] - rationale - game/models/ship.py
- [[NOTE dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent]] - rationale - game/models/ship.py
- [[.__init__()_9]] - code - game/models/board.py
- [[.__repr__()]] - code - game/models/ship.py
- [[.get_cell()]] - code - game/models/board.py
- [[.register_hit()]] - code - game/models/ship.py
- [[.reset()_7]] - code - game/models/board.py
- [[.set_cell()]] - code - game/models/board.py
- [[Board]] - code - game/models/board.py
- [[CellState]] - code - game/models/cell_state.py
- [[Enum]] - code
- [[Ship]] - code - game/models/ship.py
- [[ShipType]] - code - game/models/ship_type.py
- [[__init__.py]] - code - training/__init__.py
- [[board.py]] - code - game/models/board.py
- [[cell_state.py]] - code - game/models/cell_state.py
- [[get_fleet()]] - code - game/models/ship.py
- [[get_ship_name()]] - code - game/models/ship.py
- [[get_ship_size()]] - code - game/models/ship.py
- [[is_sunk()]] - code - game/models/ship.py
- [[ship.py]] - code - game/models/ship.py
- [[ship_type.py]] - code - game/models/ship_type.py
- [[size()]] - code - game/models/ship.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Game_State_Models
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Game Board & Actions]]

## Top bridge nodes
- [[Board]] - degree 9, connects to 1 community