# Graph Report - battleship-rl  (2026-05-13)

## Corpus Check
- 43 files · ~13,333 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 663 nodes · 1041 edges · 33 communities (26 shown, 7 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 231 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef15f17e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]

## God Nodes (most connected - your core abstractions)
1. `GameLogger` - 40 edges
2. `GameBoard` - 30 edges
3. `GameBoard` - 26 edges
4. `GameEngine` - 24 edges
5. `BayesianAgent` - 24 edges
6. `GameEngine` - 22 edges
7. `FeatureExtractor` - 21 edges
8. `BattleshipEnv` - 20 edges
9. `BaseAgent` - 20 edges
10. `BayesianAgent` - 19 edges

## Surprising Connections (you probably didn't know these)
- `GameBoard` --uses--> `Fast single-game Battleship environment for RL training.      Wraps GameBoard di`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `GameBoard` --uses--> `Take a shot at cell index `action` (row * 10 + col).          Returns:`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `BayesianAgent Baseline (Training)` --semantically_similar_to--> `Bayesian Agent Baseline`  [INFERRED] [semantically similar]
  training/README.md → analysis.md
- `init_transformer_ppo()` --calls--> `TransformerPPONet`  [INFERRED]
  training/pretrain.py → game/agents/ppo_net/__init__.py
- `Transition` --uses--> `FeatureExtractor`  [INFERRED]
  training/rollout.py → game/agents/feature_extractor.py

## Hyperedges (group relationships)
- **Two-Phase Training Pipeline: Imitation Pretraining then PPO Fine-tuning** — readme_imitation_pretraining, readme_ppo_finetuning, readme_transformerpponet [EXTRACTED 1.00]
- **Separate Trunk Design Enabling Independent Policy and Value Training** — readme_policy_trunk, readme_value_trunk, readme_separate_trunks_rationale, readme_value_warmup [EXTRACTED 0.95]
- **Three Baseline Agents Evaluated Across Ship Placement Strategies** — analysis_random_agent, analysis_hunt_agent, analysis_bayesian_agent [EXTRACTED 1.00]

## Communities (33 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (34): BaseAgent, BattleshipEnv, Take a shot at cell index `action` (row * 10 + col).          Returns:, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, BayesianAgent, Bayesian probability density agent.      Enumerates all valid ship placements on, FeatureExtractor, Return shape (4,) float32 global context vector. (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (22): format_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges() (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (32): _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges(), place_fleet_gaussian(), place_fleet_quadrant() (+24 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (21): AppLogger, main(), parse_args(), GameEngine, Orchestrates a full game of Battleship.      The game-side agent always runs in-, GameLogger, GameLogger, Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (20): Board, CellState, Enum, Board, CellState, get_ship_name(), get_ship_size(), # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (26): QAgent, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi, evaluate(), main(), parse_args(), Vanilla DQN training for the Battleship Q-learning agent.  Usage:     python tra, Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy. (+18 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (27): BattleshipEnv, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Return list of cell indices (0–99) that have not yet been shot., Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns: (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (16): Return a coordinate string (e.g. 'B5') given an observation dict., Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., Return list of cell indices (0–99) that have not yet been shot., GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (18): BayesianAgent, Remove hit cells of sunk ships from _unresolved_hits and recompute grid., Bayesian probability density agent.      Enumerates all valid ship placements on, FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Record the outcome of a shot and propagate to the internal Bayesian model., Return shape (100, 16) float32 feature array for all cells.          Calls Bayes (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (11): ABC, BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., RandomAgent, load(), Battleship agent backed by a Transformer actor-critic network.      Operates in (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (4): format_coordinate(), parse_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input.

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (28): Baseline Analysis Findings, Battleship RL Analysis Document, Bayesian Agent Baseline, Gaussian Ship Placement Strategy, Hunt Agent Baseline, Performance Target: Sub-50 Turns, Random Agent Baseline, Random Ship Placement Strategy (+20 more)

### Community 12 - "Community 12"
Cohesion: 0.1
Nodes (10): GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_, Print the board to stdout with row/col headers., Compute the list of (row, col) cells a ship would occupy., Return (True, '') if the placement is valid.         Return (False, reason) if o (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (9): Transformer actor-critic with fully separate policy and value trunks.      Polic, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe, TransformerPPONet, PolicyNet, Policy trunk: cell features → transformer encoder → per-cell log-probabilities., Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             legal_mask, Value trunk: cell + global features → scalar state value.      A learned global, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 16 - "Community 16"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (11): Architecture, code:bash (python training/pretrain.py \), code:bash (python training/ppo_train.py \), code:bash (python training/ppo_train.py --iters 500 --from-scratch), code:bash (# Play 100 automated games and report avg turns), Phase 1 — Imitation pretraining, Phase 2 — PPO fine-tuning, Reward structure (+3 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (10): Baseline Analysis, Baseline Approach, Baseline Performance, Bayesian Agent, Gaussian Placement, Hunt Agent, Random Agent, Random Placement (+2 more)

### Community 19 - "Community 19"
Cohesion: 0.29
Nodes (3): Circular experience replay buffer for DQN training., ReplayBuffer, Transition

### Community 20 - "Community 20"
Cohesion: 0.52
Nodes (6): coord_to_index(), init_transformer_ppo(), main(), parse_args(), run_training_loop(), setup_board_and_fleet()

## Knowledge Gaps
- **117 isolated node(s):** `Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.  For each`, `One epoch of value-trunk-only updates — policy trunk receives zero gradient.`, `Return a reward fn that adds alpha * Bayesian probability of the chosen cell.`, `Instantiate a reward function by name.      Args:         name:  Key from REWARD`, `Run one episode, collecting transitions. Returns (transitions, turns_to_win).` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameLogger` connect `Community 2` to `Community 0`, `Community 4`, `Community 7`, `Community 9`, `Community 10`, `Community 14`, `Community 16`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `BayesianAgent` connect `Community 0` to `Community 9`, `Community 2`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `BattleshipEnv` connect `Community 6` to `Community 8`, `Community 3`, `Community 12`, `Community 5`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `GameLogger` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameLogger` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `GameBoard` (e.g. with `GameLogger` and `GameEngine`) actually correct?**
  _`GameBoard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `GameBoard` (e.g. with `BattleshipEnv` and `GameEngine`) actually correct?**
  _`GameBoard` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `GameEngine` (e.g. with `BaseAgent` and `GameBoard`) actually correct?**
  _`GameEngine` has 6 INFERRED edges - model-reasoned connections that need verification._