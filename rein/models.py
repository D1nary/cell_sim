from __future__ import annotations

from typing import Iterable, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F
from gymnasium import spaces


def layer_init(layer: nn.Linear, std: float = 1.0) -> nn.Linear:
    """Orthogonal weight initialisation with zero bias."""
    nn.init.orthogonal_(layer.weight, std)
    if layer.bias is not None:
        nn.init.constant_(layer.bias, 0.0)
    return layer


def build_mlp(sizes: Sequence[int], activation: type[nn.Module] = nn.Tanh) -> nn.Sequential:
    layers: list[nn.Module] = []
    for i in range(len(sizes) - 1):
        layers.append(layer_init(nn.Linear(sizes[i], sizes[i + 1])))
        if i < len(sizes) - 2:
            layers.append(activation())
    return nn.Sequential(*layers)


class ActorCritic(nn.Module):
    """Shared backbone actor-critic for continuous control with Beta policy."""

    def __init__(
        self,
        observation_space: spaces.Space,
        action_space: spaces.Space,
        hidden_sizes: Iterable[int] = (128, 128),
    ) -> None:
        super().__init__()
        if not isinstance(action_space, spaces.Box):
            raise ValueError("ActorCritic currently supports Box action spaces only")
        if not isinstance(observation_space, spaces.Box):
            raise ValueError("Observation space must be Box")

        obs_dim = int(observation_space.shape[0])
        act_dim = int(action_space.shape[0])

        hidden = list(hidden_sizes)
        if not hidden:
            hidden = [64, 64]

        self.backbone = build_mlp([obs_dim, *hidden], activation=nn.Tanh)
        last_dim = hidden[-1]
        self.alpha_head = layer_init(nn.Linear(last_dim, act_dim), std=0.01)
        self.beta_head = layer_init(nn.Linear(last_dim, act_dim), std=0.01)
        self.value_head = build_mlp([obs_dim, *hidden, 1], activation=nn.Tanh)

        # Register bounds for action scaling as buffers (moved with the module)
        self.register_buffer("action_low", torch.as_tensor(action_space.low, dtype=torch.float32))
        self.register_buffer("action_high", torch.as_tensor(action_space.high, dtype=torch.float32))
        self.register_buffer("action_span", self.action_high - self.action_low)

    def _distribution(self, obs: torch.Tensor) -> torch.distributions.Independent:
        x = self.backbone(obs)
        alpha = F.softplus(self.alpha_head(x)) + 1.0
        beta = F.softplus(self.beta_head(x)) + 1.0
        base = torch.distributions.Beta(alpha, beta)
        return torch.distributions.Independent(base, 1)

    def scale_action(self, action_norm: torch.Tensor) -> torch.Tensor:
        return self.action_low + action_norm * self.action_span

    def unscale_action(self, action: torch.Tensor) -> torch.Tensor:
        return (action - self.action_low) / (self.action_span + 1e-8)

    def act(
        self,
        obs: torch.Tensor,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        dist = self._distribution(obs)
        if deterministic:
            action_norm = dist.mean
        else:
            action_norm = dist.rsample()
        action_norm = torch.clamp(action_norm, 1e-6, 1 - 1e-6)
        log_prob = dist.log_prob(action_norm)
        action = self.scale_action(action_norm)
        value = self.evaluate_value(obs)
        return action, action_norm, log_prob, value

    def evaluate_actions(
        self,
        obs: torch.Tensor,
        action_norm: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        dist = self._distribution(obs)
        log_prob = dist.log_prob(action_norm)
        entropy = dist.entropy()
        value = self.evaluate_value(obs)
        return log_prob, entropy, value

    def evaluate_value(self, obs: torch.Tensor) -> torch.Tensor:
        return self.value_head(obs).squeeze(-1)

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.evaluate_value(obs)


__all__ = ["ActorCritic", "layer_init", "build_mlp"]
