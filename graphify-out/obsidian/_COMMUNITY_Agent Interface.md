---
type: community
cohesion: 0.12
members: 26
---

# Agent Interface

**Cohesion:** 0.12 - loosely connected
**Members:** 26 nodes

## Members
- [[.__init__()_7]] - code - game/agents/hunt_agent.py
- [[._cardinal_neighbors()]] - code - game/agents/hunt_agent.py
- [[._enqueue_back()]] - code - game/agents/hunt_agent.py
- [[._enqueue_front()]] - code - game/agents/hunt_agent.py
- [[._prepend_axis_ends()]] - code - game/agents/hunt_agent.py
- [[._queue_unresolved_from_board()]] - code - game/agents/hunt_agent.py
- [[._reset_state()]] - code - game/agents/hunt_agent.py
- [[.place_fleet()_1]] - code - game/agents/base_agent.py
- [[.receive_result()_2]] - code - game/agents/base_agent.py
- [[.receive_result()_3]] - code - game/agents/hunt_agent.py
- [[.reset()_4]] - code - game/agents/base_agent.py
- [[.reset()_5]] - code - game/agents/hunt_agent.py
- [[.select_move()_3]] - code - game/agents/hunt_agent.py
- [[ABC]] - code
- [[BaseAgent_1]] - code - game/agents/base_agent.py
- [[Bayesian probability density agent.      Enumerates all valid ship placements on]] - rationale - game/agents/bayesian_agent.py
- [[Called after each move. Hook for training feedback; no-op by default.]] - rationale - game/agents/base_agent.py
- [[Hunt-and-target agent.      Search phase shoots only checkerboard cells (row+co]] - rationale - game/agents/hunt_agent.py
- [[HuntAgent]] - code - game/agents/hunt_agent.py
- [[Place this agent's fleet. Defaults to GameBoard.place_fleet().]] - rationale - game/agents/base_agent.py
- [[Prepend the two axis-aligned end cells to the front of the queue.]] - rationale - game/agents/hunt_agent.py
- [[Reset agent state for a new episode.]] - rationale - game/agents/base_agent.py
- [[Scan board for unresolved hit cells and enqueue their unshot neighbors.]] - rationale - game/agents/hunt_agent.py
- [[base_agent.py]] - code - game/agents/base_agent.py
- [[hunt_agent.py]] - code - game/agents/hunt_agent.py
- [[select_move()]] - code - game/agents/base_agent.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Agent_Interface
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Game Board & Actions]]
- 5 edges to [[_COMMUNITY_Training Environment]]
- 4 edges to [[_COMMUNITY_Agent Implementations]]
- 1 edge to [[_COMMUNITY_Game Engine Loop]]

## Top bridge nodes
- [[BaseAgent_1]] - degree 20, connects to 4 communities
- [[HuntAgent]] - degree 15, connects to 2 communities
- [[Bayesian probability density agent.      Enumerates all valid ship placements on]] - degree 3, connects to 2 communities
- [[Hunt-and-target agent.      Search phase shoots only checkerboard cells (row+co]] - degree 3, connects to 1 community
- [[Prepend the two axis-aligned end cells to the front of the queue.]] - degree 3, connects to 1 community