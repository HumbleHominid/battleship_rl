# Battleship RL

A battleship RL agent.

## Installation

```bash
conda env create -n battleship-rl -f environment.yaml
conda activate battleship-rl
pip install -e .
```

## Usage

```
python main.py [--agent {random,hunt,bayes,q-agent}]
               [--player-type {random,hunt,bayes,q-agent,websocket,terminal}]
               [--player-placement {random,manual}]
               [--player-placement-method <method>]
               [--checkpoint <path>]
               [--ws-host <host>]
               [--ws-port <port>]
               [--no-ws]
               [--headless]
               [--max-games <n>]
               [--board-size <n>]
               [--fleet-config <ship> ...]
               [--log-level {DEBUG,INFO,WARNING,ERROR}]
               [--log-boards]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--agent` | `random` | In-process agent: `random`, `hunt` (hunt-and-target), `bayes` (Bayesian probability density), or `q-agent` (trained DQN) |
| `--player-type` | `random` | Player side: any agent key, `websocket` (human via WS), or `terminal` (human via stdin) |
| `--player-placement` | `random` | Fleet placement for human players (`websocket` or `terminal`): `random` or `manual` (interactive) |
| `--player-placement-method` | — | Force a specific placement algorithm for the player when placement is random |
| `--checkpoint` | `checkpoints/q_agent.pt` | Checkpoint file for agents that support it (e.g. `q-agent`) |
| `--ws-host` | `localhost` | WebSocket server hostname |
| `--ws-port` | `8765` | WebSocket server port |
| `--no-ws` | — | Disable WebSocket server (agent-vs-agent only) |
| `--headless` | — | Suppress per-turn board display |
| `--max-games` | `100` | Number of games to play before exiting |
| `--board-size` | `10` | Board dimensions (N×N) |
| `--fleet-config` | all 5 ships | Space-separated ship names to include, e.g. `CARRIER BATTLESHIP` |
| `--log-level` | `INFO` | Logging verbosity |
| `--log-boards` | — | Log board states to the log file each turn |

**Examples:**

```bash
python main.py --agent bayes --no-ws --headless          # fast automated run
python main.py --player-type websocket --agent bayes     # human via WebSocket vs bayes agent
python main.py --no-ws --log-level DEBUG                 # debug output, no WebSocket
python main.py --player-type terminal --no-ws --max-games 1 --player-placement manual --agent q-agent  # single game against q-agent as a terminal player
```

## Training

The `q_learning` agent is trained with DQN. See [`training/README.md`](training/README.md) for full details.

```bash
python training/q_learning/q_train.py --episodes 50000 --save-path checkpoints/q_agent.pt
```

Logs are written to `training/logs/`. Checkpoints are saved to `checkpoints/`.