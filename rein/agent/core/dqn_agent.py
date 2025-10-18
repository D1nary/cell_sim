"""Deep Q-Network agent tailored to the `CellSimEnv`."""

from __future__ import annotations

import random
from typing import List, Sequence, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from torch import optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

from ...configs.defaults import AIConfig, REDUCE_LR_ON_PLATEAU_PARAMS
from ...model import QNetwork
from .replay_buffer import ReplayBuffer


def get_param() -> AIConfig:
    """Provide default AIConfig parameters without importing the CLI entry-point."""
    return AIConfig()


class DQNAgent:
    """Implements a vanilla DQN with target network and ε-greedy policy."""

    def __init__(
        self,
        state_dim: int,
        discrete_actions: Sequence[np.ndarray],
        device: torch.device,
        config: "AIConfig" | None = None,
    ) -> None:
        
        if len(discrete_actions) == 0:
            raise ValueError("discrete_actions must contain at least one action")

        self.state_dim = int(state_dim)

        # Materialise the discrete proxy for the continuous action space once.
        self.actions: List[np.ndarray] = [np.asarray(a, dtype=np.float32) for a in discrete_actions]
        self.device = device
        self.config = config or get_param()

        # Policy and target networks share architecture but their parameters diverge between updates.
        # Policy network creation
        self.policy_net = QNetwork(self.state_dim, len(self.actions), self.config.hidden_sizes).to(self.device)
        # Target network creation
        self.target_net = QNetwork(self.state_dim, len(self.actions), self.config.hidden_sizes).to(self.device)
        # Weight copy
        self.target_net.load_state_dict(self.policy_net.state_dict())
        # Target network in evaluetion mode
        self.target_net.eval()

        # Optimiser for the policy network and the replay buffer backing off-policy learning.
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.config.learning_rate)
        self.lr_scheduler = ReduceLROnPlateau(self.optimizer, **REDUCE_LR_ON_PLATEAU_PARAMS)
        self.replay_buffer = ReplayBuffer(self.config.buffer_size)

        self._step_counter = 0

    def select_action(self, state: np.ndarray, epsilon: float) -> Tuple[int, np.ndarray]:
        """Return the action index and value following an ε-greedy policy."""
        
        # Exploration branch: sample a random discrete action.
        if random.random() < epsilon:
            idx = random.randrange(len(self.actions))
            return idx, self.actions[idx]

        # Exploitation branch: pick the greedy action under the current policy network.
        state_tensor = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
            idx = int(torch.argmax(q_values, dim=1).item())
        return idx, self.actions[idx]

    def store_transition(
        self,
        state: np.ndarray,
        action_index: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Store a transition into the replay buffer."""
        self.replay_buffer.add(state, action_index, reward, next_state, done)

    def can_update(self) -> bool:
        """Return True when the buffer has enough samples for training."""
        needed = max(self.config.min_buffer_size, self.config.batch_size)
        return len(self.replay_buffer) >= needed

    def update(self) -> float | None:
        """Run a single optimization step and return the loss."""
        if not self.can_update():
            return None

        # Track how many optimisation steps we have taken for periodic target syncs.
        self._step_counter += 1
        # Sample a random mini-batch whose tensors are already placed on the agent device.
        batch = self.replay_buffer.sample(self.config.batch_size, self.device)
        states, actions, rewards, next_states, dones = batch

        # Q(s,a) values for the sampled actions under the current policy network.
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():

            # Double-DQN style target: argmax with policy net, value with target net.
            next_actions = torch.argmax(self.policy_net(next_states), dim=1, keepdim=True)
            next_q = self.target_net(next_states).gather(1, next_actions).squeeze(1)
            targets = rewards + (1.0 - dones) * self.config.gamma * next_q

        # Huber loss is robust to outliers in bootstrapped targets.
        loss = F.smooth_l1_loss(current_q, targets)
        self.optimizer.zero_grad()
        loss.backward()

        # Stabilise training by clipping large gradients when requested.
        if self.config.gradient_clip is not None:
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.config.gradient_clip)
        self.optimizer.step()

        # Periodically refresh the target network to keep the bootstrap stable.
        if self._step_counter % self.config.target_update_interval == 0:
            self.sync_target_network()

        return float(loss.item())

    def step_reward_scheduler(self, average_reward: float) -> float:
        """Adjust the learning rate when the reward plateaus or decreases."""
        self.lr_scheduler.step(average_reward)
        return float(self.optimizer.param_groups[0]["lr"])

    def sync_target_network(self) -> None:
        """Copy policy weights into the target network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def action_from_index(self, action_index: int) -> np.ndarray:
        """Convert an action index back to the continuous action vector."""
        return self.actions[int(action_index)]

    def save(self, path: str) -> None:
        """Save the policy network parameters and metadata."""
        torch.save(
            {
                "policy_state_dict": self.policy_net.state_dict(),
                "target_state_dict": self.target_net.state_dict(),
                "actions": self.actions,
            },
            path,
        )

    def load(self, path: str) -> None:
        """Load model parameters from disk."""
        # weights_only=False keeps full pickle deserialization, so trust the checkpoint source.
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.policy_net.load_state_dict(checkpoint["policy_state_dict"])
        self.target_net.load_state_dict(checkpoint["target_state_dict"])
        # Restore action discretization only when present in the checkpoint
        self.actions = [np.asarray(a, dtype=np.float32) for a in checkpoint.get("actions", self.actions)]
        self.config = checkpoint.get("config", self.config)
