from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class Transition:
    obs: np.ndarray
    action: int
    reward: float
    next_obs: np.ndarray
    done: bool


class ReplayBuffer:
    def __init__(self, capacity: int, obs_shape: Tuple[int, ...], dtype=np.float32):
        self.capacity = int(capacity)
        self.obs_shape = obs_shape
        self._obs = np.zeros((capacity, *obs_shape), dtype=dtype)
        self._next_obs = np.zeros((capacity, *obs_shape), dtype=dtype)
        self._actions = np.zeros((capacity,), dtype=np.int64)
        self._rewards = np.zeros((capacity,), dtype=np.float32)
        self._dones = np.zeros((capacity,), dtype=np.bool_)
        self._idx = 0
        self._size = 0

    def add(self, obs, action, reward, next_obs, done) -> None:
        i = self._idx
        self._obs[i] = obs
        self._actions[i] = int(action)
        self._rewards[i] = float(reward)
        self._next_obs[i] = next_obs
        self._dones[i] = bool(done)
        self._idx = (self._idx + 1) % self.capacity
        self._size = min(self._size + 1, self.capacity)

    def __len__(self) -> int:
        return self._size

    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        assert self._size >= batch_size
        idx = np.random.randint(0, self._size, size=(batch_size,), dtype=np.int64)
        return (
            self._obs[idx],
            self._actions[idx],
            self._rewards[idx],
            self._next_obs[idx],
            self._dones[idx],
        )

