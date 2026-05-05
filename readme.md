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
python main.py [--agent {random,bayes,hunt}]
               [--player-type {random,websocket}]
               [--player-placement {random,manual}]
               [--ws-host <host>]
               [--ws-port <port>]
               [--no-ws]
               [--headless]
               [--max-games <n>]
               [--log-level {DEBUG,INFO,WARNING,ERROR}]
               [--log-boards]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--agent` | `random` | Agent to use: `random` (random untried cell) or `bayes` (Bayesian probability density) or `hunt` (hunt strategy) |
| `--player-type` | `random` | `random` stub or `websocket` for a human/external player |
| `--player-placement` | `random` | Fleet placement for WS player: `random` or `manual` via WS protocol |
| `--ws-host` | `localhost` | WebSocket server hostname |
| `--ws-port` | `8765` | WebSocket server port |
| `--no-ws` | — | Disable the WebSocket server (pure terminal play) |
| `--headless` | — | Suppress per-turn board display (setup and results still shown) |
| `--max-games` | `100` | Number of games to play before exiting |
| `--log-level` | `WARNING` | Logging verbosity |
| `--log-boards` | — | Log board states at DEBUG level (implies `--log-level DEBUG`) |
**Examples:**

```bash
python main.py --agent bayes --no-ws --headless          # fast automated run
python main.py --player-type websocket --agent bayes     # human via WebSocket vs bayes agent
python main.py --no-ws --log-level DEBUG                 # debug output, no WebSocket
```

## Training

The `transformer_ppo` agent is trained in two phases. See [`training/README.md`](training/README.md) for full details.

```bash
# Phase 1 — imitation pretraining (~200k steps)
python training/pretrain.py --steps 200000 --checkpoint checkpoints/pretrain.pt

# Phase 2 — PPO fine-tuning
python training/ppo_train.py --checkpoint checkpoints/pretrain.pt --save-path checkpoints/ppo_best.pt
```

Logs are written to `training/logs/`. Checkpoints are saved to `checkpoints/`.