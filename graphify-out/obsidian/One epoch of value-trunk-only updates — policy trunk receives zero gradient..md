---
source_file: "training/ppo_train.py"
type: "rationale"
community: "Training Environment"
location: "L259"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Training_Environment
---

# One epoch of value-trunk-only updates — policy trunk receives zero gradient.

## Connections
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]
- [[TrainingLogger]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[value_warmup_update()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Training_Environment