---
source_file: "training/ppo_train.py"
type: "code"
community: "Training Environment"
location: "L46"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Training_Environment
---

# RolloutBuffer

## Connections
- [[.add()]] - `method` [EXTRACTED]
- [[.compute_returns_advantages()]] - `method` [EXTRACTED]
- [[.to_tensors()]] - `method` [EXTRACTED]
- [[BattleshipEnv]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[FeatureExtractor]] - `uses` [INFERRED]
- [[TrainingLogger]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[main()_1]] - `calls` [EXTRACTED]
- [[ppo_train.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Training_Environment