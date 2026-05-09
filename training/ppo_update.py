from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim

from game.agents.ppo_net import TransformerPPONet
from training.training_logger import TrainingLogger


def ppo_update(
    net: TransformerPPONet,
    policy_optimizer: optim.Optimizer,
    value_optimizer: optim.Optimizer,
    policy_params: list,
    value_params: list,
    batch: dict[str, torch.Tensor],
    clip_eps: float,
    entropy_coef: float,
    max_grad_norm: float,
    minibatch: int,
    n_value_epochs: int = 1,
) -> dict[str, float]:
    n = batch["cell"].shape[0]

    total_policy_loss = total_value_loss = total_entropy = 0.0
    n_updates = 0

    # Policy + value pass (n_epochs controlled by caller)
    indices = torch.randperm(n, device=batch["cell"].device)
    for start in range(0, n, minibatch):
        idx = indices[start : start + minibatch]
        cell = batch["cell"][idx]
        glob = batch["glob"][idx]
        mask = batch["mask"][idx]
        actions = batch["actions"][idx]
        old_lp = batch["old_log_probs"][idx]
        old_v = batch["old_values"][idx]
        returns = batch["returns"][idx]
        advs = batch["advantages"][idx]

        log_probs, value = net(cell, glob, mask)
        new_lp = log_probs.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Clipped PPO objective
        ratio = (new_lp - old_lp).exp()
        surr1 = ratio * advs
        surr2 = ratio.clamp(1 - clip_eps, 1 + clip_eps) * advs
        policy_loss = -torch.min(surr1, surr2).mean()

        # Entropy bonus (over legal actions only; clamp avoids 0 * -inf = NaN)
        probs = log_probs.exp()
        entropy = -(probs * log_probs.clamp(min=-100)).sum(dim=-1).mean()

        # Value loss with clipping (PPO paper §4)
        v_clipped = old_v + (value - old_v).clamp(-clip_eps, clip_eps)
        v_loss1 = (value - returns).pow(2)
        v_loss2 = (v_clipped - returns).pow(2)
        value_loss = 0.5 * torch.max(v_loss1, v_loss2).mean()

        # Policy trunk update (retain graph so value backward can follow)
        policy_optimizer.zero_grad()
        (policy_loss - entropy_coef * entropy).backward(retain_graph=True)
        nn.utils.clip_grad_norm_(policy_params, max_grad_norm)
        policy_optimizer.step()

        # Value trunk update (independent backward — no policy gradient)
        value_optimizer.zero_grad()
        value_loss.backward()
        nn.utils.clip_grad_norm_(value_params, max_grad_norm)
        value_optimizer.step()

        total_policy_loss += policy_loss.item()
        total_value_loss += value_loss.item()
        total_entropy += entropy.item()
        n_updates += 1

    # Extra value-only epochs so value head keeps pace with policy
    for _ in range(n_value_epochs - 1):
        indices = torch.randperm(n, device=batch["cell"].device)
        epoch_v_loss = 0.0
        epoch_v_updates = 0
        for start in range(0, n, minibatch):
            idx = indices[start : start + minibatch]
            _, value = net(batch["cell"][idx], batch["glob"][idx], batch["mask"][idx])
            old_v = batch["old_values"][idx]
            returns = batch["returns"][idx]
            v_clipped = old_v + (value - old_v).clamp(-clip_eps, clip_eps)
            v_loss = 0.5 * torch.max(
                (value - returns).pow(2), (v_clipped - returns).pow(2)
            ).mean()
            value_optimizer.zero_grad()
            v_loss.backward()
            nn.utils.clip_grad_norm_(value_params, max_grad_norm)
            value_optimizer.step()
            epoch_v_loss += v_loss.item()
            epoch_v_updates += 1
        total_value_loss += epoch_v_loss / max(epoch_v_updates, 1)

    k = max(n_updates, 1)
    v_k = max(n_updates * n_value_epochs, 1)
    return {
        "policy_loss": total_policy_loss / k,
        "value_loss": total_value_loss / v_k,
        "entropy": total_entropy / k,
    }


def value_warmup_update(
    net: TransformerPPONet,
    value_optimizer: optim.Optimizer,
    value_params: list,
    batch: dict[str, torch.Tensor],
    max_grad_norm: float,
    minibatch: int,
) -> float:
    """One epoch of value-trunk-only updates — policy trunk receives zero gradient."""
    n = batch["cell"].shape[0]
    indices = torch.randperm(n, device=batch["cell"].device)
    total_value_loss = 0.0
    n_updates = 0

    for start in range(0, n, minibatch):
        TrainingLogger.debug(
            f"    Update {start // minibatch + 1} / {n // minibatch + (n % minibatch > 0)}"
        )
        idx = indices[start : start + minibatch]
        _, value = net(batch["cell"][idx], batch["glob"][idx], batch["mask"][idx])
        value_loss = nn.functional.mse_loss(value, batch["returns"][idx])
        value_optimizer.zero_grad()
        value_loss.backward()
        nn.utils.clip_grad_norm_(value_params, max_grad_norm)
        value_optimizer.step()
        total_value_loss += value_loss.item()
        n_updates += 1

    return total_value_loss / max(n_updates, 1)
