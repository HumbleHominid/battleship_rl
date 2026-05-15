# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles

- Never use emojis.

## Commit Authorship

When committing code changes:
- Never add Claude as a commit author.
- Always commit as using the default git settings

## Documentation Style

When creating or updating markdown documentation files:
- **Never create .md files unless explicitly instructed.**
- **Be extremely concise** - engineers scan, they don't read novels
- **Only include essential information** - what they need to know, not what's possible to explain
- **Prefer examples over prose** - show the pattern, not the theory
- **Assume technical competence** - skip obvious explanations
- **Front-load critical info** - put warnings and key concepts first
- **Delete verbose explanations** - if it takes more than 3 sentences, it's probably too long

Default to 1-2 sentence explanations. Only expand when complexity absolutely requires it.

## Python Environment

Use the conda environment `battleship-rl` when running all python code.

## Architecture

The game is designed as a training harness for an external RL agent that connects via WebSocket. The engine runs locally; the agent is a separate process.

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `main.py` | CLI parsing, `asyncio.run()` entry |
| `game/game_engine.py` — `GameEngine` | Turn-based loop, win detection, state broadcasting |
| `game/game_board.py` — `GameBoard` | Ship placement, shot processing, coordinate parsing (`"A1"` ↔ zero-indexed row/col) |
| `game/websocket.py` — `GameWebSocketServer` | WebSocket server; one player + unlimited observers |
| `game/agents/` | In-process agents (random, hunt, bayes, q-agent) used when no WS player is connected |
| `game/models/` | Pure data: `Board` (10×10 grid), `Ship`, `ShipType`, `CellState` |

### WebSocket Protocol

Clients connect and send a handshake:
```json
{"type": "hello", "role": "observer" | "player"}
```

**Observer** clients receive `{"type": "game_state", ...}` after every move.

**Player** flow per turn:
1. Server sends `{"type": "player_view", "turn": N, "enemy_board": ..., "your_board": ...}`
2. Player replies `{"type": "move", "coordinate": "B5"}`
3. Server sends `{"type": "move_ack", "coordinate": ..., "result": ..., "ship_sunk": ..., "game_over": ...}`

Only one player is allowed per game; additional `player` connections are downgraded to observers. `GameEngine` blocks the player's turn waiting for a WS move.

### Fog of War

`_build_state_dict()` (observer view) hides agent ship positions except where hit. `_build_player_view()` sends the player their own board unobscured plus the fog-hidden agent board. This distinction matters whenever serializing or testing state output.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current


## Documentation

After any changes to the cli or training paradigm, update the readme files.