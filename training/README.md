# Training the TransformerPPO Agent

All commands should be run from the **project root**. The project uses a `pyproject.toml` so both `game` and `training` are installed as packages — run `pip install -e .` once after cloning (the conda setup does this automatically).

## Two-phase pipeline

### Phase 1 — Imitation pretraining

Trains the policy head to mimic BayesianAgent's greedy move at each step (cross-entropy / NLL loss). This gives the network a warm start before PPO.

```bash
python training/pretrain.py \
  --steps 200000 \
  --checkpoint checkpoints/pretrain.pt
```

Key options:
| Flag | Default | Description |
|------|---------|-------------|
| `--steps` | 200000 | Total gradient steps |
| `--lr` | 1e-3 | Adam learning rate |
| `--weight-decay` | 1e-4 | Adam weight decay |
| `--log-interval` | 1000 | Print loss/accuracy every N steps |
| `--save-interval` | 10000 | Save checkpoint every N steps |
| `--checkpoint` | `checkpoints/pretrain.pt` | Output checkpoint path |
| `--device` | cpu | `cpu` or `mps` or `cuda` |

Expect accuracy to climb toward ~60–80% after 200k steps (BayesianAgent is a deterministic argmax policy, so it's learnable). Loss around 1.5–2.0 indicates good convergence.

### Phase 2 — PPO fine-tuning

Loads the pretrained checkpoint and fine-tunes with on-policy PPO. Collects 8 serial episodes per iteration, then runs 4 update epochs.

```bash
python training/ppo_train.py \
  --iters 500 \
  --checkpoint checkpoints/pretrain.pt \
  --save-path checkpoints/ppo_best.pt
```

To train from random initialization (skips imitation pretraining):
```bash
python training/ppo_train.py --iters 500 --from-scratch
```

Key options:
| Flag | Default | Description |
|------|---------|-------------|
| `--iters` | 500 | Number of PPO iterations |
| `--lr` | 3e-4 | Adam learning rate |
| `--checkpoint` | — | Pretrained checkpoint to load |
| `--from-scratch` | false | Train from random init |
| `--save-path` | `checkpoints/ppo_best.pt` | Where to save the best checkpoint |
| `--eval-interval` | 25 | Evaluate every N iterations |
| `--eval-games` | 100 | Games per evaluation run |
| `--device` | cpu | `cpu` or `mps` or `cuda` |

The BayesianAgent baseline (~47 turns avg) is computed once at startup. The best checkpoint is saved whenever eval turns improve.

## Reward structure

| Event | Reward |
|-------|--------|
| Each turn | −0.1 |
| Miss | −0.1 (in addition to turn penalty) |
| Win (all ships sunk) | +10.0 |

## Running the trained agent

```bash
# Play 100 automated games and report win rate + avg turns
python main.py --agent transformer_ppo --no-ws --headless --max-games 100

# Load a specific checkpoint
python -c "
from game.agents.transformer_ppo_agent import TransformerPPOAgent
agent = TransformerPPOAgent.load('checkpoints/ppo_best.pt')
"
```

## Hyperparameter reference

PPO constants (edit `training/ppo_train.py` to change):

| Constant | Value |
|----------|-------|
| `GAMMA` | 0.99 |
| `LAM` (GAE λ) | 0.95 |
| `CLIP_EPS` | 0.2 |
| `VALUE_COEF` | 0.5 |
| `ENTROPY_COEF` | 0.01 |
| `MAX_GRAD_NORM` | 0.5 |
| `N_EPOCHS` | 4 |
| `MINIBATCH` | 256 |
| `N_EPISODES_PER_ITER` | 8 |
