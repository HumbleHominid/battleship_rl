---
source_file: "training/ppo_train.py"
type: "rationale"
community: "Training Environment"
location: "L287"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Training_Environment
---

# Return mean turns-to-win over n_games episodes (greedy policy).

## Connections
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]
- [[TrainingLogger]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[evaluate()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Training_Environment