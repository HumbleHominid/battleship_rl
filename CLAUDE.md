# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
conda env create -n battleship-rl -f environment.yaml
conda activate battleship-rl
```

## Running the Game

```bash
python main.py --mode automated          # both players use stubs (RL training mode)
python main.py --mode interactive        # human places ships and fires manually
python main.py --no-ws                   # disable WebSocket server
python main.py --ws-host 0.0.0.0 --ws-port 8765
python main.py --log-level DEBUG
```

There is no test suite yet.

## Architecture

The game is designed as a training harness for an external RL agent that connects via WebSocket. The engine runs locally; the agent is a separate process.

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `main.py` | CLI parsing, `asyncio.run()` entry |
| `game/game_engine.py` — `GameEngine` | Turn-based loop, win detection, state broadcasting |
| `game/game_board.py` — `GameBoard` | Ship placement, shot processing, coordinate parsing (`"A1"` ↔ zero-indexed row/col) |
| `game/websocket.py` — `GameWebSocketServer` | WebSocket server; one RL agent + unlimited observers |
| `game/agents/agent.py` — `RLAgent` | Stub used in automated mode when no WS agent is connected |
| `game/models/` | Pure data: `Board` (10×10 grid), `Ship`, `ShipType`, `CellState` |

### WebSocket Protocol

Clients connect and send a handshake:
```json
{"type": "hello", "role": "observer" | "rl_agent"}
```

**Observer** clients receive `{"type": "game_state", ...}` after every move (fog of war applied — ship positions hidden until hit).

**RL agent** flow per turn:
1. Server sends `{"type": "agent_view", "turn": N, "enemy_board_fog": ..., "your_board_fog": ...}`
2. Agent replies `{"type": "move", "coordinate": "B5"}`
3. Server sends `{"type": "move_ack", "coordinate": ..., "result": ..., "ship_sunk": ..., "game_over": ...}`

Only one RL agent is allowed per game; additional `rl_agent` connections are downgraded to observers. `GameEngine` blocks the agent's turn waiting for a WS move.

### Fog of War

`_build_state_dict()` (observer view) hides ship positions except where hit. `_build_agent_view_dict()` sends the agent its own board unobscured plus the fog-hidden enemy board. This distinction matters whenever serializing or testing state output.

### RLAgent Stub

`game/agents/agent.py` documents the intended interface for a real RL agent. In automated mode with no WS connection, `GameEngine` calls `agent.select_move()` (random untried cell) and `agent.receive_result()` (no-op). Methods like `connect_to_server()` raise `NotImplementedError` — the real agent is a separate process, not a subclass.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current


## Documentation

After any changes to the cli or training paradigm, update the readme files.