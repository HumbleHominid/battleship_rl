# Training the TransformerPPO Agent

All commands should be run from the **project root**. The project is installed as an editable package (`pip install -e .`) so no `PYTHONPATH` manipulation is needed.

## Two-phase pipeline

### Phase 1 — Imitation pretraining

Trains the policy head to mimic BayesianAgent's greedy move at each step (cross-entropy / NLL loss). This gives the network a warm start before PPO.

```bash
python training/pretrain.py \
  --steps 200000 \
  --checkpoint checkpoints/pretrain.pt
```

| Flag | Default | Description |
|------|---------|-------------|
| `--steps` | 200000 | Total gradient steps |
| `--lr` | 1e-3 | Peak Adam learning rate |
| `--weight-decay` | 1e-4 | Adam weight decay |
| `--warmup-steps` | 2000 | Linear LR warmup steps before cosine decay |
| `--log-interval` | 1000 | Print loss/accuracy every N steps |
| `--save-interval` | 10000 | Save checkpoint every N steps |
| `--checkpoint` | `checkpoints/pretrain.pt` | Output checkpoint path |
| `--device` | `cpu` | `cpu`, `mps`, or `cuda` |
| `--board-size` | 10 | Board dimension (N×N) |
| `--fleet-config` | all 5 ships | Space-separated ship names to include |

Expect accuracy to reach ~55–65% by step 5k and ~75–85% by 50k. Loss below 1.0 indicates good convergence.

### Phase 2 — PPO fine-tuning

Loads the pretrained checkpoint and fine-tunes with on-policy PPO. Collects 32 serial episodes per iteration, then runs 2 update epochs.

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

**Training control:**

| Flag | Default | Description |
|------|---------|-------------|
| `--iters` | 500 | Number of PPO iterations |
| `--lr` | 1e-4 | Adam learning rate |
| `--checkpoint` | — | Pretrained checkpoint to load |
| `--from-scratch` | false | Train from random init |
| `--save-path` | `checkpoints/ppo_best.pt` | Where to save the best checkpoint |
| `--eval-interval` | 25 | Evaluate every N iterations |
| `--eval-games` | 100 | Games per evaluation run |
| `--device` | `cpu` | `cpu`, `mps`, or `cuda` |

**Rollout & PPO hyperparameters:**

| Flag | Default | Description |
|------|---------|-------------|
| `--n-episodes-per-iter` | 32 | Episodes collected per iteration |
| `--n-epochs` | 2 | PPO update epochs per rollout |
| `--minibatch` | 512 | Transitions per minibatch |
| `--gamma` | 0.99 | Discount factor |
| `--lam` | 0.95 | GAE λ |
| `--clip-eps` | 0.15 | PPO clipping range |
| `--value-coef` | 0.05 | Value loss weight in total loss |
| `--entropy-coef` | 0.003 | Entropy bonus weight |
| `--max-grad-norm` | 0.5 | Gradient clipping norm |

The BayesianAgent baseline is computed over 1000 games at startup. The best checkpoint is saved whenever eval turns improve.

## Reward structure

| Event | Reward |
|-------|--------|
| Each turn | −0.1 |
| Miss | −0.1 (in addition to turn penalty) |
| Win (all ships sunk) | +10.0 |

## Running the trained agent

```bash
# Play 100 automated games and report avg turns
python main.py --agent transformer_ppo --no-ws --headless --max-games 100

# Load a specific checkpoint
python -c "
from game.agents.transformer_ppo_agent import TransformerPPOAgent
agent = TransformerPPOAgent.load('checkpoints/ppo_best.pt')
"
```
