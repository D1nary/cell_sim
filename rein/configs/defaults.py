"""Default reinforcement learning configuration values."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Dict, Any

@dataclass
class AIConfig:
    """Consolidated DQN training hyper-parameters."""

    gamma: float = 0.995  # Discount factor
    learning_rate: float = 3e-4  # Optimizer step size
    batch_size: int = 64  # Samples per training update
    buffer_size: int = 500_000  # Replay memory capacity
    min_buffer_size: int = 20_000  # Warm-up transitions before learning
    target_update_interval: int = 2_000  # Steps between target syncs
    hidden_sizes: Tuple[int, ...] = (64, 64)  # Q-network layer widths
    gradient_clip: float | None = 10.0  # Max gradient norm (None disables)

    device: str = "cuda"  # Preferred compute device

    seed: int = 1  # Random seed

    dose_bins: int = 9  # Discrete dose action bins
    wait_bins: int = 1  # Discrete wait action bins
    min_dose: float = 1.0  # Minimum radiation dose
    max_dose: float = 5.0  # Maximum radiation dose
    min_wait: int = 24  # Minimum wait time (hours)
    max_wait: int = 24  # Maximum wait time (hours)

    # episodes: int = 10_000  # Training episodes count
    episodes: int = 8_000  # Training episodes count

    growth_hours: int = 100  # Pre-episode growth duration
    max_steps: int = 2_000  # Max steps per episode
    episode_timeout_hours: int = 1_500  # Simulated hours before declaring timeout

    epsilon_start: float = 1.0  # Initial exploration rate
    epsilon_end: float = 0.05  # Final exploration rate
    epsilon_decay_steps: int = 6_00_000  # Steps to decay epsilon across 8k episodes
    save_agent_path: Path = Path("results/dqn_agent")  # Checkpoint directory
    eval_episodes: int = 10  # Greedy evaluation episodes
    save_episodes: int = 10  # Episode interval for checkpoints

    resume: bool = False  # Whether to resume training from disk
    resume_from: Path | None = None  # Optional directory for the resume checkpoint

    # Reward Aware
    reward_aware_activator: bool = False # Reward aware activator
    reward_patience: int = 15  # Episodes without gains before easing exploration
    reward_min_delta_floor: float = 1.0  # Minimum absolute reward bump
    reward_min_delta_relative: float = 0.02  # Minimum relative reward bump
    reward_epsilon_multiplier: float = 1.0  # Baseline epsilon scaling
    reward_decay_multiplier: float = 1.0  # Baseline decay scaling
    reward_epsilon_multiplier_bounds: Tuple[float, float] = (1.0, 2.0)  # Epsilon clamp range
    reward_decay_multiplier_bounds: Tuple[float, float] = (0.5, 2.5)  # Decay clamp range
    reward_epsilon_plateau_factor: float = 1.18  # Epsilon scale on plateau
    reward_epsilon_improve_factor: float = 0.95  # Epsilon scale on improvement
    reward_decay_plateau_factor: float = 1.12  # Extend decay on plateau
    reward_decay_improve_factor: float = 0.92  # Shorten decay on improvement
    reward_epsilon_max_bump_factor: float = 1.7  # Max epsilon boost factor

# Reward aware lr
REDUCE_LR_ON_PLATEAU_PARAMS: Dict[str, Any] = {
    "mode": "max",
    "factor": 0.5,
    "patience": 0,
    "threshold": 1e-3,
    "threshold_mode": "abs",
    "cooldown": 0,
    "min_lr": 1e-6,
    "verbose": False,
}


DEFAULT_CONFIG = AIConfig()
