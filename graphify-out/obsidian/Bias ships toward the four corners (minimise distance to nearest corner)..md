---
source_file: "game/fleet_placement_methods.py"
type: "rationale"
community: "Fleet Placement"
location: "L241"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Fleet_Placement
---

# Bias ships toward the four corners (minimise distance to nearest corner).

## Connections
- [[GameLogger]] - `uses` [INFERRED]
- [[PlacementTarget]] - `uses` [INFERRED]
- [[place_fleet_corners()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Fleet_Placement