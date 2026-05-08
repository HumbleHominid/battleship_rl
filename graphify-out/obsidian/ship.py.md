---
source_file: "game/models/ship.py"
type: "code"
community: "Game State Models"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Game_State_Models
---

# ship.py

## Connections
- [[NOTE ShipType enum values are priority IDs, not sizes.]] - `rationale_for` [EXTRACTED]
- [[NOTE dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent]] - `rationale_for` [EXTRACTED]
- [[Ship]] - `contains` [EXTRACTED]
- [[__init__.py]] - `imports_from` [EXTRACTED]
- [[board.py]] - `imports_from` [EXTRACTED]
- [[get_fleet()]] - `contains` [EXTRACTED]
- [[get_ship_name()]] - `contains` [EXTRACTED]
- [[get_ship_size()]] - `contains` [EXTRACTED]
- [[is_sunk()]] - `contains` [EXTRACTED]
- [[ship_type.py]] - `imports_from` [EXTRACTED]
- [[size()]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Game_State_Models