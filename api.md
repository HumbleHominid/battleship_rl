# Battleship RL — Game Server API

HTTP + WebSocket API for creating and playing Battleship games against an RL agent.

## Base URL

`http://localhost:8080` (local) or the Cloud Run service URL in production.

Interactive docs available at `/docs` (Swagger UI).

---

## REST Endpoints

### Create game

```
POST /games
```

**Body**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `agent` | string | `"q-agent"` | Agent to play against: `random`, `hunt`, `bayes`, `q-agent` |
| `player_placement` | string | `"manual"` | `"random"` (server places fleet) or `"manual"` (client places fleet over WS) |
| `player_placement_method` | string \| null | `null` | Fleet placement algorithm for the agent's fleet: `random`, `gaussian`, `spread`, `edges`, `corners`, `clustered`, `quadrant`, `dense_center`, `diagonal` |

**Response** `201`

```json
{
  "game_id": "3f2a...",
  "ws_url": "ws://localhost:8080/games/3f2a.../ws",
  "agent": "q-agent",
  "player_placement": "random"
}
```

---

### List games

```
GET /games
```

Returns an array of game status objects (see below).

---

### Get game status

```
GET /games/{game_id}
```

**Response** `200`

```json
{
  "game_id": "3f2a...",
  "status": "active",
  "agent": "q-agent",
  "player_placement": "random",
  "created_at": "2026-05-21T12:00:00+00:00",
  "turn": 4,
  "game_over": false,
  "winner": null,
  "player_score": {"sunk": 1, "hit": 4},
  "agent_score": {"sunk": 0, "hit": 2}
}
```

`status` is `"active"` or `"finished"`.

---

### Cancel game

```
DELETE /games/{game_id}
```

Cancels the game task and closes all WebSocket connections. Returns `204`.

---

## WebSocket Protocol

Connect to `ws://host/games/{game_id}/ws`.

### Handshake

After connecting, the client must send a hello message:

```json
{"type": "hello", "role": "player"}
```

or

```json
{"type": "hello", "role": "observer"}
```

Server responds:

```json
{"type": "welcome", "game_id": "3f2a...", "role": "player"}
```

Only one `player` is accepted per game. Subsequent player connections are downgraded to `observer`.

---

### Manual fleet placement (`player_placement: "manual"` only)

For each ship in the fleet the server sends a placement request:

```json
{"type": "place_ship", "ship": "CARRIER", "size": 5}
```

Client responds with a coordinate and direction:

```json
{"type": "placement", "coordinate": "C5", "direction": "right"}
```

Valid directions: `right`, `left`, `up`, `down`.

Server acknowledges:

```json
{"type": "placement_ack", "valid": true}
```

or on error:

```json
{"type": "placement_ack", "valid": false, "error": "Ship extends off the board"}
```

The server re-sends the same `place_ship` request until a valid placement is received.

---

### Game start

Once placement is complete (or immediately for `player_placement: "random"`):

```json
{"type": "game_start", "your_board": [["NONE:EMPTY", ...], ...]}
```

`your_board` is a 10×10 matrix. Each cell is `"SHIPTYPE:CELLSTATE"` (e.g. `"CARRIER:EMPTY"`, `"NONE:EMPTY"`).

---

### Player turn

When it is the player's turn, the server sends:

```json
{
  "type": "player_view",
  "turn": 5,
  "enemy_board": [["NONE:EMPTY", ...], ...],
  "your_board": [["CARRIER:EMPTY", ...], ...],
  "ships_sunk": {"by_you": 1, "against_you": 0}
}
```

`enemy_board` is fog-of-war: ship types are hidden except on `HIT` cells.

The player replies with a move:

```json
{"type": "move", "coordinate": "B5"}
```

Coordinates are `A1`–`J10` (column letter + row number).

Server confirms:

```json
{
  "type": "move_ack",
  "coordinate": "B5",
  "result": "HIT",
  "ship_hit": "DESTROYER",
  "ship_sunk": null,
  "game_over": false
}
```

`result` is `"HIT"` or `"MISS"`. `ship_sunk` is the ship name if sunk, else `null`.

---

### Game state broadcasts (observers)

After every move, all observers receive:

```json
{
  "type": "game_state",
  "game_id": "3f2a...",
  "turn": 5,
  "current_player": "agent",
  "game_over": false,
  "winner": null,
  "player_board": {
    "cells": [["CARRIER:EMPTY", ...], ...],
    "ships_remaining": 5,
    "ships_sunk": 0,
    "cells_hit": 2
  },
  "agent_board": {
    "cells": [["NONE:MISS", ...], ...],
    "ships_remaining": 4,
    "ships_sunk": 1,
    "cells_hit": 4
  },
  "scores": {
    "player": {"ships_sunk": 1, "cells_hit": 4},
    "agent": {"ships_sunk": 0, "cells_hit": 2}
  },
  "last_move": {
    "player": "player",
    "coordinate": "B5",
    "result": "HIT",
    "ship_hit": "DESTROYER",
    "ship_sunk": null
  }
}
```

---

### Ship sunk event

Broadcast to all observers whenever a ship is sunk:

```json
{"type": "ship_sunk", "attacker": "player", "ship": "DESTROYER", "turn": 5}
```

---

### Game over

```json
{
  "type": "game_over",
  "winner": "player",
  "total_turns": 42,
  "scores": {
    "player": {"ships_sunk": 5, "cells_hit": 17},
    "agent": {"ships_sunk": 3, "cells_hit": 21}
  }
}
```

`winner` is `"player"` or `"agent"`.

---

## Running locally

```bash
conda activate battleship-rl
pip install fastapi uvicorn[standard]
uvicorn server:app --reload --port 8080
```

## Docker

```bash
docker build -t battleship-rl:latest .
docker run -p 8080:8080 battleship-rl:latest
```
