# Training the Q-Learning Agent

All commands should be run from the **project root**.

## Algorithm

Vanilla DQN with a `QNetwork` (Bayesian-encoded cell + global features). Epsilon-greedy exploration with multiplicative decay.

## Training

```bash
python training/q_learning/q_train.py
python training/q_learning/q_train.py --episodes 100000 --save-path checkpoints/q_agent.pt
```

| Flag | Default | Description |
|------|---------|-------------|
| `--episodes` | 50000 | Training episodes |
| `--lr` | 1e-4 | Adam learning rate |
| `--gamma` | 0.99 | Discount factor |
| `--batch-size` | 64 | Replay buffer batch size |
| `--buffer-cap` | 100000 | Replay buffer capacity |
| `--target-sync` | 500 | Steps between target network syncs |
| `--eps-start` | 1.0 | Initial epsilon |
| `--eps-end` | 0.05 | Final epsilon |
| `--eps-decay` | 0.9999 | Multiplicative epsilon decay per episode |
| `--eval-interval` | 1000 | Episodes between evaluations |
| `--eval-games` | 200 | Games per evaluation |
| `--save-path` | `checkpoints/q_agent.pt` | Checkpoint output path |
| `--resume` | — | Resume from checkpoint |
| `--demo-games` | 0 | Bayesian agent games to pre-load into replay buffer |
| `--pretrain-games` | 0 | Games for supervised Q-value warm-start (0 = skip) |
| `--device` | `cpu` | `cpu`, `mps`, or `cuda` |
| `--reward-fn` | `default` | Reward function (`default`, `bayes`) |

## Reward structure

| Event | Reward |
|-------|--------|
| Each turn | −0.1 |
| Hit | +1.0 |
| Ship sunk | +5.0 |
| Win | +10.0 |

## Running the trained agent

```bash
python main.py --agent q_learning --checkpoint checkpoints/q_agent.pt --no-ws --headless --max-games 100
```
