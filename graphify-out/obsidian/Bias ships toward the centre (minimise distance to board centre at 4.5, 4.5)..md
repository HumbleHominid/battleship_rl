---
source_file: "game/fleet_placement_methods.py"
type: "rationale"
community: "Fleet Placement"
location: "L320"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Fleet_Placement
---

# Bias ships toward the centre (minimise distance to board centre at 4.5, 4.5).

## Connections
- [[GameLogger]] - `uses` [INFERRED]
- [[PlacementTarget]] - `uses` [INFERRED]
- [[place_fleet_dense_center()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Fleet_Placement