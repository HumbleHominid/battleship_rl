---
source_file: "game/agents/feature_extractor.py"
type: "rationale"
community: "Training Environment"
location: "L47"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Training_Environment
---

# Return shape (100, 16) float32 feature array for all cells.          Calls Bayes

## Connections
- [[.compute_cell_features()]] - `rationale_for` [EXTRACTED]
- [[BayesianAgent]] - `uses` [INFERRED]

#graphify/rationale #graphify/EXTRACTED #community/Training_Environment