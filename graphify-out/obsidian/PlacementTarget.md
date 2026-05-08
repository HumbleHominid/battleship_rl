---
source_file: "game/placement_protocol.py"
type: "code"
community: "Fleet Placement"
location: "L7"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Fleet_Placement
---

# PlacementTarget

## Connections
- [[.can_place_ship()]] - `method` [EXTRACTED]
- [[.get_placed_cells()]] - `method` [EXTRACTED]
- [[.place_ship()]] - `method` [EXTRACTED]
- [[Bias ships toward the board perimeter (minimise distance to nearest edge).]] - `uses` [INFERRED]
- [[Bias ships toward the centre (minimise distance to board centre at 4.5, 4.5).]] - `uses` [INFERRED]
- [[Bias ships toward the four corners (minimise distance to nearest corner).]] - `uses` [INFERRED]
- [[Bias ships toward the main diagonal (where row == col).]] - `uses` [INFERRED]
- [[Confine the entire fleet to one randomly chosen quadrant.]] - `uses` [INFERRED]
- [[Pack all ships tightly around a single random hotspot (opposite of spread).]] - `uses` [INFERRED]
- [[Protocol]] - `inherits` [EXTRACTED]
- [[placement_protocol.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Fleet_Placement