"""Configuration objects for RL experiments.

This module defines lightweight dataclasses with sensible defaults for
the environment and training setup. It is intentionally dependency-free
to keep bootstrapping simple.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict


@dataclass
class EnvConfig:
    # Grid and controller params
    xsize: int = 21
    ysize: int = 21
    zsize: int = 21
    sources_num: int = 20
    cradius: float = 2.0
    hradius: float = 4.0
    hcells: int = 1
    ccells: int = 1

    # Action constraints (must match rein.rl_env.CellSimEnv)
    max_dose: float = 2.0
    max_wait: int = 24

    # Discretization for DQN (number of bins per dimension)
    action_bins_dose: int = 5
    action_bins_wait: int = 6


@dataclass
class TrainConfig:
    # Reproducibility and bookkeeping
    seed: int = 42
    project_dir: Path = Path("results/rl")
    run_name: str = "debug"

    # Rollout parameters
    total_episodes: int = 10
    max_steps_per_episode: int = 200

    # Logging/Checkpointing
    save_every_episodes: int = 5
    eval_every_episodes: int = 0  # 0 disables periodic eval

    # Env config (inline for simplicity)
    env: EnvConfig = field(default_factory=EnvConfig)

    # DQN hyperparameters
    gamma: float = 0.99
    lr: float = 1e-3
    batch_size: int = 64
    buffer_size: int = 50_000
    learning_starts: int = 1000
    train_freq: int = 1
    target_update_freq: int = 1000
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay_steps: int = 20_000

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert Path to str for JSON/logging
        d["project_dir"] = str(self.project_dir)
        return d


def default_config() -> TrainConfig:
    """Return a default training config suitable for quick tests."""
    return TrainConfig()


__all__ = [
    "EnvConfig",
    "TrainConfig",
    "default_config",
]
