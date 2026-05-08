---
source_file: "training/ppo_train.py"
type: "rationale"
community: "Training Environment"
location: "L320"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Training_Environment
---

# Return mean turns-to-win for BayesianAgent (one-time reference).

## Connections
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]
- [[TrainingLogger]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[bayes_baseline()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Training_Environment