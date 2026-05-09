---
source_file: "game/models/ship_type.py"
type: "code"
community: "Game State Models"
location: "L5"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Game_State_Models
---

# ShipType

## Connections
- [[NOTE ShipType enum values are priority IDs, not sizes.]] - `uses` [INFERRED]
- [[NOTE dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent]] - `uses` [INFERRED]
- [[Board]] - `uses` [INFERRED]
- [[Enum]] - `inherits` [EXTRACTED]
- [[Ship]] - `uses` [INFERRED]
- [[ship_type.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Game_State_Models