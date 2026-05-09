---
source_file: "game/agents/feature_extractor.py"
type: "code"
community: "Training Environment"
location: "L16"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Training_Environment
---

# FeatureExtractor

## Connections
- [[.__init__()_8]] - `method` [EXTRACTED]
- [[.compute_cell_features()]] - `method` [EXTRACTED]
- [[.compute_global_features()]] - `method` [EXTRACTED]
- [[.reset()_6]] - `method` [EXTRACTED]
- [[.update()]] - `method` [EXTRACTED]
- [[Args             cell_feats  (B, 100, CELL_FEATURE_DIM)             global_fea]] - `uses` [INFERRED]
- [[Battleship agent backed by a Transformer actor-critic network.      Operates in]] - `uses` [INFERRED]
- [[BayesianAgent]] - `uses` [INFERRED]
- [[Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen]] - `rationale_for` [EXTRACTED]
- [[Imitation pretraining train TransformerPPONet to mimic BayesianAgent.  For each]] - `uses` [INFERRED]
- [[One epoch of value-trunk-only updates — policy trunk receives zero gradient.]] - `uses` [INFERRED]
- [[PPO fine-tuning for the TransformerPPO Battleship agent.  Collects on-policy rol]] - `uses` [INFERRED]
- [[Return mean turns-to-win for BayesianAgent (one-time reference).]] - `uses` [INFERRED]
- [[Return mean turns-to-win over n_games episodes (greedy policy).]] - `uses` [INFERRED]
- [[RolloutBuffer]] - `uses` [INFERRED]
- [[Run one episode, collecting transitions. Returns (transitions, turns_to_win).]] - `uses` [INFERRED]
- [[Transformer actor-critic network for Battleship with separate policy and value t]] - `uses` [INFERRED]
- [[TransformerPPOAgent]] - `uses` [INFERRED]
- [[TransformerPPONet]] - `uses` [INFERRED]
- [[Transition]] - `uses` [INFERRED]
- [[feature_extractor.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Training_Environment