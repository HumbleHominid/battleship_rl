---
source_file: "game/agents/base_agent.py"
type: "rationale"
community: "Agent Interface"
location: "L21"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Agent_Interface
---

# Called after each move. Hook for training feedback; no-op by default.

## Connections
- [[.receive_result()_2]] - `rationale_for` [EXTRACTED]
- [[GameBoard]] - `uses` [INFERRED]

#graphify/rationale #graphify/EXTRACTED #community/Agent_Interface