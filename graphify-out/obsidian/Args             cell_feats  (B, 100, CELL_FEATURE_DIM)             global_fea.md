---
source_file: "game/agents/transformer_ppo_agent.py"
type: "rationale"
community: "Training Environment"
location: "L78"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Training_Environment
---

# Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             global_fea

## Connections
- [[.forward()]] - `rationale_for` [EXTRACTED]
- [[BaseAgent_1]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/Training_Environment