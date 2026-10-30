# Battleship RL

A battleship RL agent.

## Installation

```bash
conda env create -n battleship-rl -f environment.yaml
conda activate battleship-rl
pip install -e .
```

## Game server

The FastAPI server lets a WebSocket client play against an agent. See [`api.md`](api.md).

```bash
uvicorn server:app --reload --port 8080
```

## Evaluating agents

`main.py` plays agents against each other and prints win rates and turn counts.

```
python main.py [--agent {random,hunt,bayes,q-agent}]
               [--player-type {random,hunt,bayes,q-agent}]
               [--checkpoint <path>]
               [--headless]
               [--max-games <n>]
               [--log-level {DEBUG,INFO,WARNING,ERROR}]
               [--log-boards]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--agent` | `random` | Agent under evaluation: `random`, `hunt` (hunt-and-target), `bayes` (Bayesian probability density), or `q-agent` (trained DQN) |
| `--player-type` | `random` | Opposing agent, same choices as `--agent` |
| `--checkpoint` | `checkpoints/q_agent.pt` | Checkpoint file for the `q-agent` |
| `--headless` | — | Suppress per-turn board display |
| `--max-games` | `100` | Number of games to play before exiting |
| `--log-level` | `INFO` | Console logging verbosity |
| `--log-boards` | — | Log board states to the log file each turn |

```bash
python main.py --agent q-agent --player-type bayes --headless --max-games 100
```

## Training

The `q-agent` is trained with DQN. See [`training/README.md`](training/README.md) for full details.

```bash
python training/q_train.py --episodes 50000 --save-path checkpoints/q_agent.pt
```

Logs are written to `logs/`. Checkpoints are saved to `checkpoints/`.
