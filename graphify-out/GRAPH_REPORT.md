# Graph Report - .  (2026-05-08)

## Corpus Check
- 28 files · ~10,221 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 291 nodes · 498 edges · 14 communities detected
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.51)
- Token cost: 1,850 input · 980 output

## God Nodes (most connected - your core abstractions)
1. `GameLogger` - 40 edges
2. `GameBoard` - 30 edges
3. `BayesianAgent` - 24 edges
4. `GameEngine` - 22 edges
5. `FeatureExtractor` - 21 edges
6. `BaseAgent` - 20 edges
7. `BattleshipEnv` - 16 edges
8. `GameWebSocketServer` - 15 edges
9. `TransformerPPONet` - 15 edges
10. `HuntAgent` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Fast single-game Battleship environment for RL training.      Wraps GameBoard di` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py
- `Take a shot at cell index `action` (row * 10 + col).          Returns:` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py
- `Bayesian Agent Baseline` --semantically_similar_to--> `BayesianAgent Baseline (Training)`  [INFERRED] [semantically similar]
  analysis.md → training/README.md
- `BattleshipEnv` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py
- `Return list of cell indices (0–99) that have not yet been shot.` --uses--> `GameBoard`  [INFERRED]
  training/battleship_env.py → game/game_board.py

## Hyperedges (group relationships)
- **Two-Phase Training Pipeline: Imitation Pretraining then PPO Fine-tuning** — readme_imitation_pretraining, readme_ppo_finetuning, readme_transformerpponet [EXTRACTED 1.00]
- **Separate Trunk Design Enabling Independent Policy and Value Training** — readme_policy_trunk, readme_value_trunk, readme_separate_trunks_rationale, readme_value_warmup [EXTRACTED 0.95]
- **Three Baseline Agents Evaluated Across Ship Placement Strategies** — analysis_random_agent, analysis_hunt_agent, analysis_bayesian_agent [EXTRACTED 1.00]

## Communities

### Community 0 - "Game Board & Actions"
Cohesion: 0.06
Nodes (27): Return a coordinate string (e.g. 'B5') given an observation dict., Return list of cell indices (0–99) that have not yet been shot., GameBoard, Return the Ship occupying this cell, or None., Process an incoming shot.         Returns (CellState.HIT, Ship) on hit, (CellSta, Return all (row, col) pairs not yet shot (EMPTY or ship still there)., Serialize board to a 10x10 list of 'SHIPTYPE:CELLSTATE' strings.         If fog_, Print the board to stdout with row/col headers. (+19 more)

### Community 1 - "Training Environment"
Cohesion: 0.08
Nodes (29): BattleshipEnv, Take a shot at cell index `action` (row * 10 + col).          Returns:, Fast single-game Battleship environment for RL training.      Wraps GameBoard di, BayesianAgent, FeatureExtractor, Return shape (4,) float32 global context vector., Computes per-cell (100, 16) and global (4,) features for the TransformerPPO agen, Record the outcome of a shot and propagate to the internal Bayesian model. (+21 more)

### Community 2 - "Fleet Placement"
Cohesion: 0.11
Nodes (20): _best_scored_candidate(), place_fleet_clustered(), place_fleet_corners(), place_fleet_dense_center(), place_fleet_diagonal(), place_fleet_edges(), place_fleet_gaussian(), place_fleet_quadrant() (+12 more)

### Community 3 - "Agent Analysis & Baselines"
Cohesion: 0.09
Nodes (28): Baseline Analysis Findings, Battleship RL Analysis Document, Bayesian Agent Baseline, Gaussian Ship Placement Strategy, Hunt Agent Baseline, Performance Target: Sub-50 Turns, Random Agent Baseline, Random Ship Placement Strategy (+20 more)

### Community 4 - "Agent Interface"
Cohesion: 0.12
Nodes (10): ABC, BaseAgent, Place this agent's fleet. Defaults to GameBoard.place_fleet()., Called after each move. Hook for training feedback; no-op by default., Reset agent state for a new episode., Bayesian probability density agent.      Enumerates all valid ship placements on, HuntAgent, Hunt-and-target agent.      Search phase: shoots only checkerboard cells (row+co (+2 more)

### Community 5 - "Game State Models"
Cohesion: 0.15
Nodes (10): Board, CellState, Enum, get_ship_name(), get_ship_size(), # NOTE: dicts are ordered in Python 3.7+, _SHIP_SIZES.keys() is consistent, # NOTE: ShipType enum values are priority IDs, not sizes., Ship (+2 more)

### Community 6 - "Coordinate & Game Core"
Cohesion: 0.1
Nodes (4): format_coordinate(), parse_coordinate(), Format zero-indexed (row, col) to 'A1'-'J10'., Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input.

### Community 7 - "Game Engine Loop"
Cohesion: 0.22
Nodes (1): GameEngine

### Community 8 - "Agent Implementations"
Cohesion: 0.13
Nodes (5): BaseAgent, RandomAgent, load(), Battleship agent backed by a Transformer actor-critic network.      Operates in, TransformerPPOAgent

### Community 9 - "Pretraining Pipeline"
Cohesion: 0.52
Nodes (6): coord_to_index(), init_transformer_ppo(), main(), parse_args(), run_training_loop(), setup_board_and_fleet()

### Community 10 - "Training Logger"
Cohesion: 0.29
Nodes (0): 

### Community 11 - "CLI Entry Point"
Cohesion: 1.0
Nodes (2): main(), parse_args()

### Community 12 - "Training Logger"
Cohesion: 1.0
Nodes (1): Configure handlers. Called once from main.py at process start.

### Community 13 - "Training Logger"
Cohesion: 1.0
Nodes (1): Flush and close all file handlers. Call before archiving the log file.

## Knowledge Gaps
- **16 isolated node(s):** `Statically accessible logger. Call GameLogger.info() / .warn() / .error() / .deb`, `Configure handlers. Called once from main.py at process start.`, `Flush and close all file handlers. Call before archiving the log file.`, `Parse 'A1'-'J10' to zero-indexed (row, col). Raises ValueError on bad input.`, `Format zero-indexed (row, col) to 'A1'-'J10'.` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Training Logger`** (1 nodes): `Configure handlers. Called once from main.py at process start.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Training Logger`** (1 nodes): `Flush and close all file handlers. Call before archiving the log file.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameLogger` connect `Game Board & Actions` to `Training Environment`, `Fleet Placement`, `Agent Interface`, `Game State Models`, `Coordinate & Game Core`, `Game Engine Loop`, `Agent Implementations`?**
  _High betweenness centrality (0.416) - this node is a cross-community bridge._
- **Why does `BayesianAgent` connect `Training Environment` to `Agent Implementations`, `Game Board & Actions`, `Agent Interface`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `GameBoard` connect `Game Board & Actions` to `Training Environment`, `Agent Interface`, `Coordinate & Game Core`, `Game Engine Loop`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `GameLogger` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameLogger` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `GameBoard` (e.g. with `GameEngine` and `Orchestrates a full game of Battleship.      The game-side agent always runs in-`) actually correct?**
  _`GameBoard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `BayesianAgent` (e.g. with `BaseAgent` and `GameLogger`) actually correct?**
  _`BayesianAgent` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `GameEngine` (e.g. with `BaseAgent` and `GameBoard`) actually correct?**
  _`GameEngine` has 4 INFERRED edges - model-reasoned connections that need verification._