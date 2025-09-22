from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class RolloutSample:
    observations: torch.Tensor
    actions: torch.Tensor
    log_probs: torch.Tensor
    advantages: torch.Tensor
    returns: torch.Tensor
    values: torch.Tensor


class RolloutBuffer:
    """Fixed-size rollout storage for on-policy algorithms like PPO."""

    def __init__(
        self,
        rollout_steps: int,
        obs_dim: int,
        action_dim: int,
        device: torch.device,
    ) -> None:
        self.rollout_steps = rollout_steps
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.device = device
        self.reset()

    def reset(self) -> None:
        self.observations = torch.zeros((self.rollout_steps, self.obs_dim), device=self.device)
        self.actions = torch.zeros((self.rollout_steps, self.action_dim), device=self.device)
        self.log_probs = torch.zeros(self.rollout_steps, device=self.device)
        self.rewards = torch.zeros(self.rollout_steps, device=self.device)
        self.dones = torch.zeros(self.rollout_steps, device=self.device)
        self.values = torch.zeros(self.rollout_steps, device=self.device)
        self.advantages = torch.zeros(self.rollout_steps, device=self.device)
        self.returns = torch.zeros(self.rollout_steps, device=self.device)
        self.pos = 0

    def add(
        self,
        obs: torch.Tensor,
        action_norm: torch.Tensor,
        log_prob: torch.Tensor,
        reward: float,
        done: bool,
        value: torch.Tensor,
    ) -> None:
        if self.pos >= self.rollout_steps:
            raise RuntimeError("RolloutBuffer overflow: call reset() before reuse")
        self.observations[self.pos] = obs
        self.actions[self.pos] = action_norm
        self.log_probs[self.pos] = log_prob
        self.rewards[self.pos] = float(reward)
        self.dones[self.pos] = float(done)
        self.values[self.pos] = value
        self.pos += 1

    def compute_returns_and_advantages(
        self,
        last_value: torch.Tensor,
        last_done: bool,
        gamma: float,
        gae_lambda: float,
    ) -> None:
        advantages = torch.zeros_like(self.rewards)
        last_advantage = 0.0
        last_value_scalar = float(last_value)
        last_done_flag = 1.0 if last_done else 0.0

        for step in reversed(range(self.rollout_steps)):
            if step == self.rollout_steps - 1:
                next_non_terminal = 1.0 - last_done_flag
                next_value = last_value_scalar
            else:
                next_non_terminal = 1.0 - self.dones[step + 1]
                next_value = float(self.values[step + 1])

            delta = (
                self.rewards[step]
                + gamma * next_value * next_non_terminal
                - self.values[step]
            )
            last_advantage = (
                delta
                + gamma * gae_lambda * next_non_terminal * last_advantage
            )
            advantages[step] = last_advantage

        self.advantages = advantages
        self.returns = self.advantages + self.values

    def iter_minibatches(self, batch_size: int):
        if self.pos != self.rollout_steps:
            raise RuntimeError("RolloutBuffer not full; collect more samples before training")
        indices = torch.randperm(self.rollout_steps, device=self.device)
        for start in range(0, self.rollout_steps, batch_size):
            end = start + batch_size
            mb_inds = indices[start:end]
            yield RolloutSample(
                observations=self.observations[mb_inds],
                actions=self.actions[mb_inds],
                log_probs=self.log_probs[mb_inds],
                advantages=self.advantages[mb_inds],
                returns=self.returns[mb_inds],
                values=self.values[mb_inds],
            )


__all__ = ["RolloutBuffer", "RolloutSample"]
