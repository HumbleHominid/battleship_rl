---
type: community
cohesion: 0.08
members: 55
---

# Training Environment

**Cohesion:** 0.08 - loosely connected
**Members:** 55 nodes

## Members
- [[.__init__()_10]] - code - training/battleship_env.py
- [[.__init__()_4]] - code - game/agents/bayesian_agent.py
- [[.__init__()_8]] - code - game/agents/feature_extractor.py
- [[._get_obs()]] - code - training/battleship_env.py
- [[._initialize_placements()]] - code - game/agents/bayesian_agent.py
- [[._recompute_grid()]] - code - game/agents/bayesian_agent.py
- [[.add()]] - code - training/ppo_train.py
- [[.compute_cell_features()]] - code - game/agents/feature_extractor.py
- [[.compute_global_features()]] - code - game/agents/feature_extractor.py
- [[.compute_returns_advantages()]] - code - training/ppo_train.py
- [[.forward()]] - code - game/agents/transformer_ppo_agent.py
- [[.receive_result()]] - code - game/agents/bayesian_agent.py
- [[.reset()_8]] - code - training/battleship_env.py
- [[.reset()_2]] - code - game/agents/bayesian_agent.py
- [[.reset()_6]] - code - game/agents/feature_extractor.py
- [[.select_move()_1]] - code - game/agents/bayesian_agent.py
- [[.step()]] - code - training/battleship_env.py
- [[.to_tensors()]] - code - training/ppo_train.py
- [[.update()]] - code - game/agents/feature_extractor.py
- [[Args             cell_feats  (B, 100, CELL_FEATURE_DIM)             global_fea]] - rationale - game/agents/transformer_ppo_agent.py
- [[BattleshipEnv]] - code - training/battleship_env.py
- [[BayesianAgent]] - code - game/agents/bayesian_agent.py
- [[Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen]] - rationale - game/agents/feature_extractor.py
- [[Fast single-game Battleship environment for RL training.      Wraps GameBoard di]] - rationale - training/battleship_env.py
- [[FeatureExtractor]] - code - game/agents/feature_extractor.py
- [[Imitation pretraining train TransformerPPONet to mimic BayesianAgent.  For each]] - rationale - training/pretrain.py
- [[One epoch of value-trunk-only updates — policy trunk receives zero gradient.]] - rationale - training/ppo_train.py
- [[PPO fine-tuning for the TransformerPPO Battleship agent.  Collects on-policy rol]] - rationale - training/ppo_train.py
- [[Record the outcome of a shot and propagate to the internal Bayesian model.]] - rationale - game/agents/feature_extractor.py
- [[Return mean turns-to-win for BayesianAgent (one-time reference).]] - rationale - training/ppo_train.py
- [[Return mean turns-to-win over n_games episodes (greedy policy).]] - rationale - training/ppo_train.py
- [[Return shape (100, 16) float32 feature array for all cells.          Calls Bayes]] - rationale - game/agents/feature_extractor.py
- [[Return shape (4,) float32 global context vector.]] - rationale - game/agents/feature_extractor.py
- [[RolloutBuffer]] - code - training/ppo_train.py
- [[Run one episode, collecting transitions. Returns (transitions, turns_to_win).]] - rationale - training/ppo_train.py
- [[Statically accessible logger for training scripts.      Call TrainingLogger.setu]] - rationale - training/training_logger.py
- [[Take a shot at cell index `action` (row  10 + col).          Returns]] - rationale - training/battleship_env.py
- [[TrainingLogger]] - code - training/training_logger.py
- [[Transformer actor-critic network for Battleship with separate policy and value t]] - rationale - game/agents/transformer_ppo_agent.py
- [[TransformerPPONet]] - code - game/agents/transformer_ppo_agent.py
- [[Transition]] - code - training/ppo_train.py
- [[battleship_env.py]] - code - training/battleship_env.py
- [[bayes_baseline()]] - code - training/ppo_train.py
- [[bayesian_agent.py]] - code - game/agents/bayesian_agent.py
- [[collect_episode()]] - code - training/ppo_train.py
- [[coord_to_index()_1]] - code - training/ppo_train.py
- [[done()]] - code - training/battleship_env.py
- [[evaluate()]] - code - training/ppo_train.py
- [[feature_extractor.py]] - code - game/agents/feature_extractor.py
- [[main()_1]] - code - training/ppo_train.py
- [[parse_args()_1]] - code - training/ppo_train.py
- [[ppo_train.py]] - code - training/ppo_train.py
- [[ppo_update()]] - code - training/ppo_train.py
- [[turn()_1]] - code - training/battleship_env.py
- [[value_warmup_update()]] - code - training/ppo_train.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Training_Environment
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Agent Implementations]]
- 5 edges to [[_COMMUNITY_Game Board & Actions]]
- 5 edges to [[_COMMUNITY_Agent Interface]]
- 1 edge to [[_COMMUNITY_Pretraining Pipeline]]
- 1 edge to [[_COMMUNITY_Training Logger]]

## Top bridge nodes
- [[BayesianAgent]] - degree 24, connects to 3 communities
- [[TransformerPPONet]] - degree 15, connects to 2 communities
- [[FeatureExtractor]] - degree 21, connects to 1 community
- [[BattleshipEnv]] - degree 16, connects to 1 community
- [[TrainingLogger]] - degree 10, connects to 1 community