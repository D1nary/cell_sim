"""DQN policy and simple baselines.

Includes a NumPy RandomPolicy and a PyTorch DQN agent over a Discrete
action space produced by a discretization wrapper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

# Optional dependency, but required for DQN
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except Exception as _e:  # pragma: no cover - import time guard
    torch = None  # type: ignore
    nn = None  # type: ignore
    optim = None  # type: ignore


class BasePolicy:
    """Abstract policy interface."""

    def reset(self) -> None:
        """Reset any per-episode state (optional)."""
        return None

    def act(self, obs: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """Return an action for the given observation."""
        raise NotImplementedError

    def save(self, path: str) -> None:  # noqa: ARG002
        """Persist policy parameters (optional)."""
        return None

    def load(self, path: str) -> None:  # noqa: ARG002
        """Load policy parameters (optional)."""
        return None


@dataclass
class RandomPolicy(BasePolicy):
    """Samples uniformly from the env's action space."""

    low: np.ndarray
    high: np.ndarray

    def act(self, obs: np.ndarray, deterministic: bool = False) -> np.ndarray:  # noqa: ARG002
        return np.random.uniform(self.low, self.high).astype(np.float32)


__all__ = [
    "BasePolicy",
    "RandomPolicy",
    "QNetwork",
    "DQNAgent",
]


class QNetwork(nn.Module):  # type: ignore[misc]
    def __init__(self, obs_dim: int, n_actions: int, hidden: Tuple[int, int] = (128, 128)):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden[0]),
            nn.ReLU(),
            nn.Linear(hidden[0], hidden[1]),
            nn.ReLU(),
            nn.Linear(hidden[1], n_actions),
        )

    def forward(self, x):  # type: ignore[override]
        return self.net(x)


@dataclass
class DQNAgent(BasePolicy):
    obs_dim: int
    n_actions: int
    lr: float = 1e-3
    gamma: float = 0.99
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay_steps: int = 20_000
    device: str = "cpu"

    def __post_init__(self) -> None:
        if torch is None:
            raise ImportError("PyTorch is required for DQNAgent")
        self.q_net = QNetwork(self.obs_dim, self.n_actions).to(self.device)
        self.target_net = QNetwork(self.obs_dim, self.n_actions).to(self.device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.opt = optim.Adam(self.q_net.parameters(), lr=self.lr)
        self._step = 0

    def epsilon(self) -> float:
        frac = min(1.0, max(0.0, self._step / float(max(1, self.eps_decay_steps))))
        return float(self.eps_start + frac * (self.eps_end - self.eps_start))

    def act(self, obs: np.ndarray, deterministic: bool = False) -> np.ndarray:  # type: ignore[override]
        self._step += 1
        if not deterministic and np.random.rand() < self.epsilon():
            a = np.random.randint(0, self.n_actions, dtype=np.int64)
            return np.asarray(a, dtype=np.int64)
        with torch.no_grad():
            x = torch.tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            q = self.q_net(x)
            a = int(torch.argmax(q, dim=1).item())
        return np.asarray(a, dtype=np.int64)

    def update(self, batch, target_net, gamma: float):
        obs, actions, rewards, next_obs, dones = batch
        obs_t = torch.tensor(obs, dtype=torch.float32, device=self.device)
        act_t = torch.tensor(actions, dtype=torch.int64, device=self.device).unsqueeze(1)
        rew_t = torch.tensor(rewards, dtype=torch.float32, device=self.device).unsqueeze(1)
        nxt_t = torch.tensor(next_obs, dtype=torch.float32, device=self.device)
        done_t = torch.tensor(dones.astype(np.float32), dtype=torch.float32, device=self.device).unsqueeze(1)

        # Compute current Q estimates
        q = self.q_net(obs_t).gather(1, act_t)

        # Compute target Q values
        with torch.no_grad():
            max_next_q = target_net(nxt_t).max(dim=1, keepdim=True)[0]
            target = rew_t + (1.0 - done_t) * gamma * max_next_q

        loss = torch.nn.functional.mse_loss(q, target)
        self.opt.zero_grad(set_to_none=True)
        loss.backward()
        self.opt.step()
        return float(loss.item())

    def sync_target(self):
        self.target_net.load_state_dict(self.q_net.state_dict())

    def save(self, path: str) -> None:  # type: ignore[override]
        torch.save({
            "q_net": self.q_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "step": self._step,
        }, path)

    def load(self, path: str) -> None:  # type: ignore[override]
        state = torch.load(path, map_location=self.device)
        self.q_net.load_state_dict(state["q_net"]) 
        self.target_net.load_state_dict(state["target_net"]) 
        self._step = int(state.get("step", 0))
