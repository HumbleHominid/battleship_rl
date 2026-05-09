---
source_file: "game/fleet_placement_methods.py"
type: "rationale"
community: "Fleet Placement"
location: "L325"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Fleet_Placement
---

# Bias ships toward the main diagonal (where row == col).

## Connections
- [[GameLogger]] - `uses` [INFERRED]
- [[PlacementTarget]] - `uses` [INFERRED]
- [[place_fleet_diagonal()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Fleet_Placement