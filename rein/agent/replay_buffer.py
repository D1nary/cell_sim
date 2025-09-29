"""Experience replay buffer used by the DQN agent."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Tuple

import numpy as np
import torch


@dataclass
class Transition:
    """Single transition stored in the replay buffer."""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


class ReplayBuffer:
    """Fixed-size buffer that stores transitions for off-policy learning."""

    def __init__(self, capacity: int) -> None:
        self.capacity = int(capacity)
        # Bounded deque drops the oldest transition once capacity is exceeded.
        self._buffer: Deque[Transition] = deque(maxlen=self.capacity)

    def __len__(self) -> int:
        return len(self._buffer)

    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Append a new transition to the buffer."""
        # Store a normalized snapshot so later mutations of the original arrays do not leak in.
        self._buffer.append(
            Transition(
                state=np.asarray(state, dtype=np.float32),
                action=int(action),
                reward=float(reward),
                next_state=np.asarray(next_state, dtype=np.float32),
                done=bool(done),
            )
        )

    def sample(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, ...]:
        """Sample a mini-batch and return tensors on the requested device."""
        if len(self._buffer) < batch_size:
            raise ValueError("ReplayBuffer has fewer samples than the requested batch_size")

        # Draw unique indices to avoid duplicate transitions within the batch.
        indices = np.random.choice(len(self._buffer), size=batch_size, replace=False)
        batch = [self._buffer[idx] for idx in indices]

        states = torch.as_tensor(np.stack([t.state for t in batch], axis=0), device=device)
        actions = torch.as_tensor([t.action for t in batch], device=device, dtype=torch.long)
        rewards = torch.as_tensor([t.reward for t in batch], device=device, dtype=torch.float32)
        next_states = torch.as_tensor(
            np.stack([t.next_state for t in batch], axis=0),
            device=device,
        )
        # Cast to float so masks can be used in arithmetic when computing targets.
        dones = torch.as_tensor([t.done for t in batch], device=device, dtype=torch.float32)
        return states, actions, rewards, next_states, dones
