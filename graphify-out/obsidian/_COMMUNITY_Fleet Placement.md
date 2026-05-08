---
type: community
cohesion: 0.11
members: 29
---

# Fleet Placement

**Cohesion:** 0.11 - loosely connected
**Members:** 29 nodes

## Members
- [[.can_place_ship()]] - code - game/placement_protocol.py
- [[.get_placed_cells()]] - code - game/placement_protocol.py
- [[.place_ship()]] - code - game/placement_protocol.py
- [[Bias ships toward the board perimeter (minimise distance to nearest edge).]] - rationale - game/fleet_placement_methods.py
- [[Bias ships toward the centre (minimise distance to board centre at 4.5, 4.5).]] - rationale - game/fleet_placement_methods.py
- [[Bias ships toward the four corners (minimise distance to nearest corner).]] - rationale - game/fleet_placement_methods.py
- [[Bias ships toward the main diagonal (where row == col).]] - rationale - game/fleet_placement_methods.py
- [[Confine the entire fleet to one randomly chosen quadrant.]] - rationale - game/fleet_placement_methods.py
- [[Pack all ships tightly around a single random hotspot (opposite of spread).]] - rationale - game/fleet_placement_methods.py
- [[PlacementTarget]] - code - game/placement_protocol.py
- [[Protocol]] - code
- [[_best_scored_candidate()]] - code - game/fleet_placement_methods.py
- [[_center_dist()]] - code - game/fleet_placement_methods.py
- [[_corner_dist()]] - code - game/fleet_placement_methods.py
- [[_diag_dist()]] - code - game/fleet_placement_methods.py
- [[_edge_dist()]] - code - game/fleet_placement_methods.py
- [[_place_with_score()]] - code - game/fleet_placement_methods.py
- [[_placement_error()]] - code - game/fleet_placement_methods.py
- [[fleet_placement_methods.py]] - code - game/fleet_placement_methods.py
- [[place_fleet_clustered()]] - code - game/fleet_placement_methods.py
- [[place_fleet_corners()]] - code - game/fleet_placement_methods.py
- [[place_fleet_dense_center()]] - code - game/fleet_placement_methods.py
- [[place_fleet_diagonal()]] - code - game/fleet_placement_methods.py
- [[place_fleet_edges()]] - code - game/fleet_placement_methods.py
- [[place_fleet_gaussian()]] - code - game/fleet_placement_methods.py
- [[place_fleet_quadrant()]] - code - game/fleet_placement_methods.py
- [[place_fleet_random()]] - code - game/fleet_placement_methods.py
- [[place_fleet_spread()]] - code - game/fleet_placement_methods.py
- [[placement_protocol.py]] - code - game/placement_protocol.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fleet_Placement
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Game Board & Actions]]
- 3 edges to [[_COMMUNITY_Coordinate & Game Core]]

## Top bridge nodes
- [[fleet_placement_methods.py]] - degree 20, connects to 1 community
- [[Bias ships toward the board perimeter (minimise distance to nearest edge).]] - degree 3, connects to 1 community
- [[Bias ships toward the four corners (minimise distance to nearest corner).]] - degree 3, connects to 1 community
- [[Pack all ships tightly around a single random hotspot (opposite of spread).]] - degree 3, connects to 1 community
- [[Confine the entire fleet to one randomly chosen quadrant.]] - degree 3, connects to 1 community