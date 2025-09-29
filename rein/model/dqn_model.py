"""PyTorch modules used by the DQN agent."""

from __future__ import annotations

from typing import Iterable

import torch
from torch import nn


class QNetwork(nn.Module):
    """Feed-forward network that outputs Q-values for each discrete action."""

    def __init__(
        self,
        input_dim: int,  # dimensionality of the state
        output_dim: int,  # number of discrete actions
        hidden_sizes: Iterable[int] = (128, 128),  # widths of hidden layers
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        last_dim = input_dim

        # Build a stack of linear → ReLU blocks for each requested hidden size.
        for size in hidden_sizes:
            layers.append(nn.Linear(last_dim, int(size)))
            layers.append(nn.ReLU())
            last_dim = int(size)
            
        # Last layer maps features to raw Q-values for every action.
        layers.append(nn.Linear(last_dim, output_dim))
        self.net = nn.Sequential(*layers)

        self._init_weights()

    def _init_weights(self) -> None:
        """Apply Xavier initialization to the linear layers."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                # Xavier init keeps activations stable when propagating through the MLP.
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return Q-values for the provided batch of states."""
        return self.net(x)
