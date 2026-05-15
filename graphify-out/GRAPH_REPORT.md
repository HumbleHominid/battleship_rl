# Graph Report - battleship-rl  (2026-05-15)

## Corpus Check
- 31 files · ~10,318 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 716 nodes · 1135 edges · 48 communities (40 shown, 8 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a25d8685`
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
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]

## God Nodes (most connected - your core abstractions)
1. `GameLogger` - 40 edges
2. `GameBoard` - 30 edges
3. `BattleshipEnv` - 26 edges
4. `GameBoard` - 26 edges
5. `GameEngine` - 25 edges
6. `BayesianAgent` - 24 edges
7. `GameEngine` - 22 edges
8. `BayesianAgent` - 21 edges
9. `FeatureExtractor` - 21 edges
10. `BaseAgent` - 20 edges

## Surprising Connections (you probably didn't know these)
- `GameBoard` --uses--> `Fast single-game Battleship environment for RL training.      Wraps GameBoard di`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `GameBoard` --uses--> `Take a shot at cell index `action` (row * 10 + col).          Returns:`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `BayesianAgent Baseline (Training)` --semantically_similar_to--> `Bayesian Agent Baseline`  [INFERRED] [semantically similar]
  training/README.md → analysis.md
- `BattleshipEnv` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py
- `BattleshipEnv` --uses--> `GameLogger`  [INFERRED]
  training/battleship_env.py → game/game_logger.py

## Hyperedges (group relationships)
- **Two-Phase Training Pipeline: Imitation Pretraining then PPO Fine-tuning** — readme_imitation_pretraining, readme_ppo_finetuning, readme_transformerpponet [EXTRACTED 1.00]
- **Separate Trunk Design Enabling Independent Policy and Value Training** — readme_policy_trunk, readme_value_trunk, readme_separate_trunks_rationale, readme_value_warmup [EXTRACTED 0.95]
- **Three Baseline Agents Evaluated Across Ship Placement Strategies** — analysis_random_agent, analysis_hunt_agent, analysis_bayesian_agent [EXTRACTED 1.00]

## Communities (48 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (31): BattleshipEnv, Take a shot at cell index `action` (row * 10 + col).          Returns:, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, BayesianAgent, Bayesian probability density agent.      Enumerates all valid ship placements on, FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen (+23 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (25): format_coordinate(), parse_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input., _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center() (+17 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (27): Return a coordinate string (e.g. 'B5') given an observation dict., Return list of cell indices (0–99) that have not yet been shot., GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_, Print the board to stdout with row/col headers. (+19 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (20): Board, CellState, Enum, Board, CellState, get_ship_name(), get_ship_size(), # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (17): ABC, BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default. (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (20): format_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges() (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (18): RandomAgent, AppLogger, GameLogger, GameLogger, Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb, GameWebSocketServer, Receive move and placement commands from the player and enqueue them., Embedded WebSocket server that:       - Broadcasts game state to all connected o (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (20): GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_ (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (28): Baseline Analysis Findings, Battleship RL Analysis Document, Bayesian Agent Baseline, Gaussian Ship Placement Strategy, Hunt Agent Baseline, Performance Target: Sub-50 Turns, Random Agent Baseline, Random Ship Placement Strategy (+20 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (16): Transformer actor-critic with fully separate policy and value trunks.      Polic, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe, TransformerPPONet, PolicyNet, Policy trunk: cell features → transformer encoder → per-cell log-probabilities., Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             legal_mask, Value trunk: cell + global features → scalar state value.      A learned global, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (7): Record the outcome of a shot and propagate to the internal Bayesian model., main(), parse_args(), parse_coordinate(), Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input., GameEngine, Orchestrates a full game of Battleship.      The game-side agent always runs in-

### Community 12 - "Community 12"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (14): Algorithm, Architecture, code:bash (python training/q_learning/q_train.py), code:bash (python main.py --agent q-agent --checkpoint checkpoints/q_ag), code:bash (python training/ppo_train.py --iters 500 --from-scratch), code:bash (# Play 100 automated games and report avg turns), Phase 1 — Imitation pretraining, Phase 2 — PPO fine-tuning (+6 more)

### Community 14 - "Community 14"
Cohesion: 0.21
Nodes (5): BayesianAgent, Remove hit cells of sunk ships from _unresolved_hits and recompute grid., Remove hit cells of sunk ships from _unresolved_hits and recompute grid., Bayesian probability density agent.      Enumerates all valid ship placements on, Explicitly initialize placements and compute the starting grid.

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (10): BattleshipEnv, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Args: (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (12): fill_demo_buffer(), main(), parse_args(), pretrain_supervised(), Vanilla DQN training for the Battleship Q-learning agent.  Usage:     python tra, Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla, Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla, Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla (+4 more)

### Community 17 - "Community 17"
Cohesion: 0.26
Nodes (11): evaluate(), fill_demo_buffer(), main(), parse_args(), pretrain_supervised(), Vanilla DQN training for the Battleship Q-learning agent.  Usage:     python tra, Return mean turns-to-win over n_games episodes with greedy policy., Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla (+3 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (10): Baseline Analysis, Baseline Approach, Baseline Performance, Bayesian Agent, Gaussian Placement, Hunt Agent, Random Agent, Random Placement (+2 more)

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (3): load(), Battleship agent backed by a Transformer actor-critic network.      Operates in, TransformerPPOAgent

### Community 20 - "Community 20"
Cohesion: 0.29
Nodes (3): Circular experience replay buffer for DQN training., ReplayBuffer, Transition

### Community 21 - "Community 21"
Cohesion: 0.25
Nodes (4): BayesEncoder, Stateful encoder that wraps BayesianAgent to produce Q-network features.      Mu, Encode game observation into feature tensors.          Returns:             cell, Encode game observation into feature tensors.          Returns:             cell

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (6): bayes_augment_reward(), make_reward_fn(), Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Instantiate a reward function by name.      Args:         name:  Key from REWARD, Instantiate a reward function by name.      Args:         name:  Key from REWARD

### Community 23 - "Community 23"
Cohesion: 0.29
Nodes (3): Circular experience replay buffer for DQN training., ReplayBuffer, Transition

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (4): FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Return shape (100, 16) float32 feature array for all cells.          Calls Bayes

### Community 25 - "Community 25"
Cohesion: 0.32
Nodes (4): collect_episode(), Run one episode, collecting transitions. Returns (transitions, turns_to_win)., RolloutBuffer, Transition

### Community 26 - "Community 26"
Cohesion: 0.32
Nodes (6): main(), parse_args(), PPO fine-tuning for the TransformerPPO Battleship agent.  Collects on-policy rol, ppo_update(), One epoch of value-trunk-only updates — policy trunk receives zero gradient., value_warmup_update()

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (3): QAgent, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (3): QNetwork, MLP Q-network for Battleship.      Maps a board state to a Q-value for each of t, CNN Q-network for Battleship.      Treats the 10x10 board as a spatial grid and

### Community 29 - "Community 29"
Cohesion: 0.29
Nodes (7): evaluate(), Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy.

### Community 30 - "Community 30"
Cohesion: 0.29
Nodes (6): Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot.

### Community 31 - "Community 31"
Cohesion: 0.52
Nodes (6): coord_to_index(), init_transformer_ppo(), main(), parse_args(), run_training_loop(), setup_board_and_fleet()

### Community 33 - "Community 33"
Cohesion: 0.4
Nodes (4): bayes_augment_reward(), make_reward_fn(), Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Instantiate a reward function by name.      Args:         name:  Key from REWARD

### Community 34 - "Community 34"
Cohesion: 0.4
Nodes (4): bayes_baseline(), evaluate(), Return mean turns-to-win over n_games episodes (greedy policy)., Return mean turns-to-win for BayesianAgent (one-time reference).

## Knowledge Gaps
- **146 isolated node(s):** `Return a reward fn that adds alpha * Bayesian probability of the chosen cell.`, `Instantiate a reward function by name.      Args:         name:  Key from REWARD`, `Fast single-game Battleship environment for RL training.      Wraps GameBoard di`, `Take a shot at cell index `action` (row * 10 + col).          Args:`, `Return list of cell indices (0–99) that have not yet been shot.` (+141 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameLogger` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 11`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `BattleshipEnv` connect `Community 15` to `Community 34`, `Community 36`, `Community 6`, `Community 7`, `Community 9`, `Community 16`, `Community 17`, `Community 25`, `Community 26`, `Community 29`, `Community 30`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `BayesianAgent` connect `Community 0` to `Community 2`, `Community 4`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `GameLogger` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameLogger` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `GameBoard` (e.g. with `GameLogger` and `GameEngine`) actually correct?**
  _`GameBoard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `BattleshipEnv` (e.g. with `GameBoard` and `GameLogger`) actually correct?**
  _`BattleshipEnv` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `GameBoard` (e.g. with `BattleshipEnv` and `GameEngine`) actually correct?**
  _`GameBoard` has 7 INFERRED edges - model-reasoned connections that need verification._