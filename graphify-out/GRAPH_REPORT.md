# Graph Report - battleship-rl  (2026-05-21)

## Corpus Check
- 31 files · ~11,157 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 769 nodes · 1200 edges · 50 communities (41 shown, 9 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 260 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c7ffe8c`
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
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 49|Community 49]]

## God Nodes (most connected - your core abstractions)
1. `GameLogger` - 40 edges
2. `GameBoard` - 30 edges
3. `GameEngine` - 27 edges
4. `BattleshipEnv` - 26 edges
5. `GameBoard` - 26 edges
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
- `GameBoard` --uses--> `Return list of cell indices (0–99) that have not yet been shot.`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `BayesianAgent Baseline (Training)` --semantically_similar_to--> `Bayesian Agent Baseline`  [INFERRED] [semantically similar]
  training/README.md → analysis.md
- `BattleshipEnv` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py

## Hyperedges (group relationships)
- **Two-Phase Training Pipeline: Imitation Pretraining then PPO Fine-tuning** — readme_imitation_pretraining, readme_ppo_finetuning, readme_transformerpponet [EXTRACTED 1.00]
- **Separate Trunk Design Enabling Independent Policy and Value Training** — readme_policy_trunk, readme_value_trunk, readme_separate_trunks_rationale, readme_value_warmup [EXTRACTED 0.95]
- **Three Baseline Agents Evaluated Across Ship Placement Strategies** — analysis_random_agent, analysis_hunt_agent, analysis_bayesian_agent [EXTRACTED 1.00]

## Communities (50 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (8): BayesianAgent, Bayesian probability density agent.      Enumerates all valid ship placements on, FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Record the outcome of a shot and propagate to the internal Bayesian model., Return shape (100, 16) float32 feature array for all cells.          Calls Bayes, Return mean turns-to-win for BayesianAgent (one-time reference).

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (24): BayesianAgent, Remove hit cells of sunk ships from _unresolved_hits and recompute grid., Remove hit cells of sunk ships from _unresolved_hits and recompute grid., Bayesian probability density agent.      Enumerates all valid ship placements on, Explicitly initialize placements and compute the starting grid., FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (22): format_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., _best_scored_candidate(), place_fleet_clustered(), place_fleet_cognitive_human(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal() (+14 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (20): Board, CellState, Enum, Board, CellState, get_ship_name(), get_ship_size(), # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (30): GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return the Ship occupying this cell, or None., Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there). (+22 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (21): GameWebSocketServer, Receive move and placement commands from the player and enqueue them., Receive move and placement commands from the player and enqueue them., Embedded WebSocket server that:       - Broadcasts game state to all connected o, Register an observer and hold its connection open until disconnect., Register an observer and hold its connection open until disconnect., Serialize state_dict to JSON and send to all connected observers., Serialize state_dict to JSON and send to all connected observers and the player. (+13 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (14): _init_global_state(), main(), _make_engine(), parse_args(), Run n_games headless agent-vs-random games and return per-game stats.      Safe, Run n_games headless agent-vs-random games and return per-game stats.      Safe, run_game(), run_games_headless() (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (28): Baseline Analysis Findings, Battleship RL Analysis Document, Bayesian Agent Baseline, Gaussian Ship Placement Strategy, Hunt Agent Baseline, Performance Target: Sub-50 Turns, Random Agent Baseline, Random Ship Placement Strategy (+20 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (16): Transformer actor-critic with fully separate policy and value trunks.      Polic, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe, TransformerPPONet, PolicyNet, Policy trunk: cell features → transformer encoder → per-cell log-probabilities., Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             legal_mask, Value trunk: cell + global features → scalar state value.      A learned global, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (25): format_coordinate(), parse_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input., _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center() (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (29): Return a coordinate string (e.g. 'B5') given an observation dict., Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there). (+21 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (9): ABC, BaseAgent, Return mean turns-to-win over n_games episodes (greedy policy)., load(), Battleship agent backed by a Transformer actor-critic network.      Operates in, Transformer actor-critic network for Battleship with separate policy and value t, Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             global_fea, TransformerPPOAgent (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (5): FastAPIWebSocketAdapter, Drop-in replacement for GameWebSocketServer that accepts FastAPI/Starlette     W, Called by GameEngine as asyncio.create_task(adapter.start()).         Suspends u, Called by GameEngine in its finally block. Closes all open connections., Called by the FastAPI WS endpoint for every new connection.         Performs the

### Community 14 - "Community 14"
Cohesion: 0.17
Nodes (11): BattleshipEnv, Take a shot at cell index `action` (row * 10 + col).          Returns:, Return list of cell indices (0–99) that have not yet been shot., Fast single-game Battleship environment for RL training.      Wraps GameBoard di, collect_episode(), PPO fine-tuning for the TransformerPPO Battleship agent.  Collects on-policy rol, Run one episode, collecting transitions. Returns (transitions, turns_to_win)., One epoch of value-trunk-only updates — policy trunk receives zero gradient. (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.22
Nodes (4): BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode.

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (10): BattleshipEnv, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Args: (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.19
Nodes (14): evaluate(), fill_demo_buffer(), main(), parse_args(), pretrain_supervised(), Vanilla DQN training for the Battleship Q-learning agent.  Usage:     python tra, Return mean turns-to-win over n_games episodes with greedy policy., Return mean turns-to-win over n_games episodes with greedy policy. (+6 more)

### Community 18 - "Community 18"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 19 - "Community 19"
Cohesion: 0.17
Nodes (14): Algorithm, Architecture, code:bash (python training/q_learning/q_train.py), code:bash (python main.py --agent q-agent --checkpoint checkpoints/q_ag), code:bash (python training/ppo_train.py --iters 500 --from-scratch), code:bash (# Play 100 automated games and report avg turns), Phase 1 — Imitation pretraining, Phase 2 — PPO fine-tuning (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (16): evaluate(), main(), parse_args(), pretrain_supervised(), Vanilla DQN training for the Battleship Q-learning agent.  Usage:     python tra, Return mean turns-to-win over n_games episodes with greedy policy., Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla, Warm-start net by regression: Q[i] ≈ Bayesian occupancy probability[i].      Pla (+8 more)

### Community 21 - "Community 21"
Cohesion: 0.30
Nodes (7): bayes_baseline(), evaluate(), main(), parse_args(), ppo_update(), RolloutBuffer, value_warmup_update()

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (6): bayes_augment_reward(), make_reward_fn(), Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Instantiate a reward function by name.      Args:         name:  Key from REWARD, Instantiate a reward function by name.      Args:         name:  Key from REWARD

### Community 23 - "Community 23"
Cohesion: 0.29
Nodes (3): Circular experience replay buffer for DQN training., ReplayBuffer, Transition

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (4): BayesEncoder, Stateful encoder that wraps BayesianAgent to produce Q-network features.      Mu, Encode game observation into feature tensors.          Returns:             cell, Encode game observation into feature tensors.          Returns:             cell

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (3): Circular experience replay buffer for DQN training., ReplayBuffer, Transition

### Community 27 - "Community 27"
Cohesion: 0.18
Nodes (10): Baseline Analysis, Baseline Approach, Baseline Performance, Bayesian Agent, Gaussian Placement, Hunt Agent, Random Agent, Random Placement (+2 more)

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (6): Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot.

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (5): RandomAgent, AppLogger, GameLogger, GameLogger, Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (6): QAgent, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi, QNetwork, MLP Q-network for Battleship.      Maps a board state to a Q-value for each of t, CNN Q-network for Battleship.      Treats the 10x10 board as a spatial grid and

### Community 31 - "Community 31"
Cohesion: 0.43
Nodes (7): coord_to_index(), init_transformer_ppo(), main(), parse_args(), Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.  For each, run_training_loop(), setup_board_and_fleet()

### Community 33 - "Community 33"
Cohesion: 0.40
Nodes (4): bayes_augment_reward(), make_reward_fn(), Return a reward fn that adds alpha * Bayesian probability of the chosen cell., Instantiate a reward function by name.      Args:         name:  Key from REWARD

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (5): fill_demo_buffer(), Pre-populate replay buffer with Bayesian agent game transitions., Pre-populate replay buffer with Bayesian agent game transitions., legal_mask_from_obs(), Return (100,) bool array — True for cells that have not yet been shot.

### Community 45 - "Community 45"
Cohesion: 0.25
Nodes (3): load(), Battleship agent backed by a Transformer actor-critic network.      Operates in, TransformerPPOAgent

## Knowledge Gaps
- **20 isolated node(s):** `Algorithm`, `Random Agent`, `Hunt Agent`, `Bayesian Agent`, `Random Placement` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameLogger` connect `Community 11` to `Community 0`, `Community 3`, `Community 5`, `Community 10`, `Community 47`, `Community 26`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `GameLogger` connect `Community 29` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 13`, `Community 16`, `Community 18`, `Community 30`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Why does `BattleshipEnv` connect `Community 16` to `Community 1`, `Community 4`, `Community 9`, `Community 42`, `Community 17`, `Community 20`, `Community 28`, `Community 29`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `GameLogger` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameLogger` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `GameBoard` (e.g. with `GameLogger` and `GameEngine`) actually correct?**
  _`GameBoard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `GameEngine` (e.g. with `GameBoard` and `GameLogger`) actually correct?**
  _`GameEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `BattleshipEnv` (e.g. with `GameBoard` and `GameLogger`) actually correct?**
  _`BattleshipEnv` has 16 INFERRED edges - model-reasoned connections that need verification._