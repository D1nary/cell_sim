from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass
class PPOConfig:
    """Configuration container for PPO training."""

    total_timesteps: int = 200_000
    rollout_steps: int = 2_048
    learning_rate: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_coef: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    update_epochs: int = 10
    minibatch_size: int = 256
    seed: int = 42
    device: str = "auto"
    log_interval: int = 1_000
    eval_interval: int = 10_000
    num_eval_episodes: int = 5
    target_success_rate: float = 0.8
    early_stop_patience: int = 5
    hidden_sizes: Tuple[int, ...] = (128, 128)
    checkpoint_path: Path = field(
        default_factory=lambda: Path("results/checkpoints/best_agent.pt")
    )

    def ensure_minibatch(self) -> None:
        """Adjust minibatch size to stay within rollout length."""
        if self.minibatch_size > self.rollout_steps:
            self.minibatch_size = self.rollout_steps


__all__ = ["PPOConfig"]
