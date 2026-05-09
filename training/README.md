# Training the TransformerPPO Agent

All commands should be run from the **project root**. The project is installed as an editable package (`pip install -e .`) so no `PYTHONPATH` manipulation is needed.

## Architecture

`TransformerPPONet` uses **separate policy and value trunks** — no shared parameters between the two paths:

- **Policy trunk**: `policy_cell_proj` → 4-layer Transformer encoder → `policy_head` (per-cell logit)
- **Value trunk**: `value_cell_proj` + `global_proj` → 4-layer Transformer encoder → `value_head` (global token)

Keeping the trunks separate means value gradients never corrupt pretrained policy weights, and the value encoder has full board visibility (all 101 tokens) rather than just the global summary token.

## Two-phase pipeline

### Phase 1 — Imitation pretraining

Trains the **policy trunk** to mimic BayesianAgent's greedy move at each step (cross-entropy / NLL loss). The value trunk is not touched. This gives the policy a warm start before PPO.

```bash
python training/pretrain.py \
  --steps 200000 \
  --checkpoint checkpoints/pretrain.pt
```

| Flag | Default | Description |
|------|---------|-------------|
| `--steps` | 200000 | Total gradient steps |
| `--lr` | 1e-3 | Peak Adam learning rate (policy trunk only) |
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

Loads the pretrained checkpoint and fine-tunes with on-policy PPO. Policy and value trunks are updated with independent optimizers — no gradient interference between them.

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
| `--policy-lr` | 1e-4 | Adam learning rate for policy trunk |
| `--value-lr` | 1e-4 | Adam learning rate for value trunk |
| `--checkpoint` | — | Pretrained checkpoint to load |
| `--from-scratch` | false | Train from random init |
| `--save-path` | `checkpoints/ppo_best.pt` | Where to save the best checkpoint |
| `--eval-interval` | 25 | Evaluate every N iterations |
| `--eval-games` | 100 | Games per evaluation run |
| `--device` | `cpu` | `cpu`, `mps`, or `cuda` |
| `--value-warmup-iters` | 100 | Value-trunk-only iterations before PPO begins (0 to skip) |

**Rollout & PPO hyperparameters:**

| Flag | Default | Description |
|------|---------|-------------|
| `--n-episodes-per-iter` | 32 | Episodes collected per iteration |
| `--n-epochs` | 2 | PPO update epochs per rollout |
| `--minibatch` | 512 | Transitions per minibatch |
| `--gamma` | 0.99 | Discount factor |
| `--lam` | 0.95 | GAE λ |
| `--clip-eps` | 0.15 | PPO clipping range |
| `--entropy-coef` | 0.003 | Entropy bonus weight |
| `--max-grad-norm` | 0.5 | Gradient clipping norm |

The BayesianAgent baseline is computed over 1000 games at startup. The best checkpoint is saved whenever eval turns improve.

Before the main PPO loop, a value-warmup phase (`--value-warmup-iters`) trains only the value trunk using rollouts from the pretrained policy. Because the trunks are separate, this warmup never touches policy weights — entropy stays near its pretrained value throughout. Returns are batch-normalised to zero mean / unit variance before the value MSE, keeping value loss in the O(1) range throughout training.

**Note:** Pretrained checkpoints from the old shared-trunk architecture are not compatible. Re-run `pretrain.py` after any architecture change.

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
