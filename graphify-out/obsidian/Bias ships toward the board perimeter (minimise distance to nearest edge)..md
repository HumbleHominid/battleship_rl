---
source_file: "game/fleet_placement_methods.py"
type: "rationale"
community: "Fleet Placement"
location: "L236"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Fleet_Placement
---

# Bias ships toward the board perimeter (minimise distance to nearest edge).

## Connections
- [[GameLogger]] - `uses` [INFERRED]
- [[PlacementTarget]] - `uses` [INFERRED]
- [[place_fleet_edges()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Fleet_Placement