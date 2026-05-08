---
source_file: "game/agents/hunt_agent.py"
type: "rationale"
community: "Agent Interface"
location: "L95"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Agent_Interface
---

# Scan board for unresolved hit cells and enqueue their unshot neighbors.

## Connections
- [[._queue_unresolved_from_board()]] - `rationale_for` [EXTRACTED]
- [[BaseAgent_1]] - `uses` [INFERRED]
- [[GameLogger]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Agent_Interface