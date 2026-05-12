# Graph Report - battleship-rl  (2026-05-12)

## Corpus Check
- 42 files · ~12,727 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 643 nodes · 1017 edges · 41 communities (33 shown, 8 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 229 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec659098`
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
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]

## God Nodes (most connected - your core abstractions)
1. `GameLogger` - 40 edges
2. `GameBoard` - 30 edges
3. `GameBoard` - 26 edges
4. `GameEngine` - 24 edges
5. `BayesianAgent` - 24 edges
6. `GameEngine` - 22 edges
7. `FeatureExtractor` - 21 edges
8. `BaseAgent` - 20 edges
9. `BattleshipEnv` - 19 edges
10. `BayesianAgent` - 18 edges

## Surprising Connections (you probably didn't know these)
- `GameBoard` --uses--> `Fast single-game Battleship environment for RL training.      Wraps GameBoard di`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `GameBoard` --uses--> `Take a shot at cell index `action` (row * 10 + col).          Returns:`  [INFERRED]
  game/game_board.py → training/battleship_env.py
- `BayesianAgent Baseline (Training)` --semantically_similar_to--> `Bayesian Agent Baseline`  [INFERRED] [semantically similar]
  training/README.md → analysis.md
- `coord_to_index()` --calls--> `parse_coordinate()`  [INFERRED]
  training/pretrain.py → game/coordinate_methods.py
- `init_transformer_ppo()` --calls--> `TransformerPPONet`  [INFERRED]
  training/pretrain.py → game/agents/ppo_net/__init__.py

## Hyperedges (group relationships)
- **Two-Phase Training Pipeline: Imitation Pretraining then PPO Fine-tuning** — readme_imitation_pretraining, readme_ppo_finetuning, readme_transformerpponet [EXTRACTED 1.00]
- **Separate Trunk Design Enabling Independent Policy and Value Training** — readme_policy_trunk, readme_value_trunk, readme_separate_trunks_rationale, readme_value_warmup [EXTRACTED 0.95]
- **Three Baseline Agents Evaluated Across Ship Placement Strategies** — analysis_random_agent, analysis_hunt_agent, analysis_bayesian_agent [EXTRACTED 1.00]

## Communities (41 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (30): BattleshipEnv, Take a shot at cell index `action` (row * 10 + col).          Returns:, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, BayesianAgent, FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Record the outcome of a shot and propagate to the internal Bayesian model. (+22 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (22): format_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges() (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (20): Board, CellState, Enum, Board, CellState, get_ship_name(), get_ship_size(), # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (18): RandomAgent, AppLogger, GameLogger, GameLogger, Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb, GameWebSocketServer, Receive move and placement commands from the player and enqueue them., Embedded WebSocket server that:       - Broadcasts game state to all connected o (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (18): QAgent, Battleship agent backed by a Q-network (DQN).      Operates in greedy mode (epsi, Circular experience replay buffer for DQN training., ReplayBuffer, Transition, evaluate(), main(), parse_args() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (14): ABC, BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., BaseAgent, Bayesian probability density agent.      Enumerates all valid ship placements on, HuntAgent (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (28): Baseline Analysis Findings, Battleship RL Analysis Document, Bayesian Agent Baseline, Gaussian Ship Placement Strategy, Hunt Agent Baseline, Performance Target: Sub-50 Turns, Random Agent Baseline, Random Ship Placement Strategy (+20 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (19): _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges(), place_fleet_gaussian(), place_fleet_quadrant() (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (11): GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_, Print the board to stdout with row/col headers., Compute the list of (row, col) cells a ship would occupy., Return (True, '') if the placement is valid.         Return (False, reason) if o (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (9): Return a coordinate string (e.g. 'B5') given an observation dict., Return list of cell indices (0–99) that have not yet been shot., GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_, Print the board to stdout with row/col headers. (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (13): GameLogger, Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb, GameWebSocketServer, Receive move and placement commands from the player and enqueue them., Embedded WebSocket server that:       - Broadcasts game state to all connected o, Register an observer and hold its connection open until disconnect., Serialize state_dict to JSON and send to all connected observers., Send a JSON message to the connected player. No-op if none connected. (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.1
Nodes (4): format_coordinate(), parse_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input.

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (4): main(), parse_args(), GameEngine, Orchestrates a full game of Battleship.      The game-side agent always runs in-

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (9): Transformer actor-critic with fully separate policy and value trunks.      Polic, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe, TransformerPPONet, PolicyNet, Policy trunk: cell features → transformer encoder → per-cell log-probabilities., Args:             cell_feats:  (B, 100, CELL_FEATURE_DIM)             legal_mask, Value trunk: cell + global features → scalar state value.      A learned global, Args:             cell_feats:   (B, 100, CELL_FEATURE_DIM)             global_fe (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (7): BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., load(), Battleship agent backed by a Transformer actor-critic network.      Operates in, TransformerPPOAgent

### Community 16 - "Community 16"
Cohesion: 0.23
Nodes (4): HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co, Prepend the two axis-aligned end cells to the front of the queue., Scan board for unresolved hit cells and enqueue their unshot neighbors.

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (7): BattleshipEnv, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Take a shot at cell index `action` (row * 10 + col).          Returns:, Fast single-game Battleship environment for RL training.      Wraps GameBoard di

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (11): Architecture, code:bash (python training/pretrain.py \), code:bash (python training/ppo_train.py \), code:bash (python training/ppo_train.py --iters 500 --from-scratch), code:bash (# Play 100 automated games and report avg turns), Phase 1 — Imitation pretraining, Phase 2 — PPO fine-tuning, Reward structure (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (10): Baseline Analysis, Baseline Approach, Baseline Performance, Bayesian Agent, Gaussian Placement, Hunt Agent, Random Agent, Random Placement (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (7): Record the outcome of a shot and propagate to the internal Bayesian model., parse_coordinate(), Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input., bayes_baseline(), evaluate(), Return mean turns-to-win over n_games episodes (greedy policy)., Return mean turns-to-win for BayesianAgent (one-time reference).

### Community 22 - "Community 22"
Cohesion: 0.22
Nodes (4): FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Return shape (100, 16) float32 feature array for all cells.          Calls Bayes

### Community 23 - "Community 23"
Cohesion: 0.43
Nodes (7): coord_to_index(), init_transformer_ppo(), main(), parse_args(), Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.  For each, run_training_loop(), setup_board_and_fleet()

### Community 24 - "Community 24"
Cohesion: 0.32
Nodes (4): collect_episode(), Run one episode, collecting transitions. Returns (transitions, turns_to_win)., RolloutBuffer, Transition

### Community 25 - "Community 25"
Cohesion: 0.32
Nodes (6): main(), parse_args(), PPO fine-tuning for the TransformerPPO Battleship agent.  Collects on-policy rol, ppo_update(), One epoch of value-trunk-only updates — policy trunk receives zero gradient., value_warmup_update()

### Community 26 - "Community 26"
Cohesion: 0.29
Nodes (4): Compute the list of (row, col) cells a ship would occupy., Return (True, '') if the placement is valid.         Return (False, reason) if o, Place a ship on the board. Raises ValueError if placement is invalid.         Re, Convenience wrapper: place_ship_from_str(ShipType.CARRIER, 'A1', 'right').

### Community 27 - "Community 27"
Cohesion: 0.52
Nodes (6): coord_to_index(), init_transformer_ppo(), main(), parse_args(), run_training_loop(), setup_board_and_fleet()

### Community 29 - "Community 29"
Cohesion: 0.5
Nodes (3): Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot., Return list of cell indices (0–99) that have not yet been shot.

## Knowledge Gaps
- **107 isolated node(s):** `Imitation pretraining: train TransformerPPONet to mimic BayesianAgent.  For each`, `One epoch of value-trunk-only updates — policy trunk receives zero gradient.`, `Run one episode, collecting transitions. Returns (transitions, turns_to_win).`, `Fast single-game Battleship environment for RL training.      Wraps GameBoard di`, `Take a shot at cell index `action` (row * 10 + col).          Returns:` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameLogger` connect `Community 10` to `Community 0`, `Community 2`, `Community 5`, `Community 7`, `Community 9`, `Community 11`, `Community 15`, `Community 26`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `BayesianAgent` connect `Community 0` to `Community 10`, `Community 5`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `GameLogger` connect `Community 3` to `Community 1`, `Community 2`, `Community 8`, `Community 12`, `Community 16`, `Community 17`, `Community 20`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `GameLogger` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameLogger` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `GameBoard` (e.g. with `GameLogger` and `GameEngine`) actually correct?**
  _`GameBoard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `GameBoard` (e.g. with `BattleshipEnv` and `GameEngine`) actually correct?**
  _`GameBoard` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `GameEngine` (e.g. with `BaseAgent` and `GameBoard`) actually correct?**
  _`GameEngine` has 6 INFERRED edges - model-reasoned connections that need verification._