---
source_file: "training/ppo_train.py"
type: "rationale"
community: "Training Environment"
location: "L111"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Training_Environment
---

# Run one episode, collecting transitions. Returns (transitions, turns_to_win).

## Connections
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]
- [[TrainingLogger]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[collect_episode()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Training_Environment