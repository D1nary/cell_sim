"""Utilities for saving agent checkpoints, replay buffers, and run metadata."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING

import numpy as np
import torch

from .replay_buffer import ReplayBuffer

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from main import AIConfig


__all__ = [
    "checkpoint_path_for_episode",
    "final_checkpoint_path",
    "collect_rng_state",
    "save_replay_buffer_checkpoint",
    "serialise_config",
    "save_training_config",
    "save_episode_metrics",
]


def checkpoint_path_for_episode(base_path: Path, episode: int) -> Path:
    """Generate a unique checkpoint path for the given episode."""
    if base_path.suffix:
        directory = base_path.parent
        stem = base_path.stem
        suffix = base_path.suffix
    else:
        directory = base_path.parent if base_path.parent != base_path else Path(".")
        stem = base_path.name
        suffix = ".pt"

    if stem in {"", ".", ".."}:
        stem = "checkpoint"

    return directory / f"{stem}_ep{episode:04d}{suffix}"


def final_checkpoint_path(base_path: Path, final_stem: str) -> Path:
    """Return the final checkpoint path under the same directory as base_path."""
    directory = base_path.parent
    suffix = base_path.suffix or ".pt"
    return directory / f"{final_stem}{suffix}"


def collect_rng_state() -> Dict[str, Any]:
    """Snapshot RNG states needed to reproduce replay sampling."""
    rng_state: Dict[str, Any] = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        rng_state["torch_cuda"] = torch.cuda.get_rng_state_all()
    return rng_state


def _serialise_transitions(transitions: Iterable) -> List[Dict[str, Any]]:
    """Convert replay buffer transitions into JSON/pickle-friendly structures."""
    serialised: List[Dict[str, Any]] = []
    for transition in transitions:
        serialised.append(
            {
                "state": transition.state,
                "action": transition.action,
                "reward": transition.reward,
                "next_state": transition.next_state,
                "done": transition.done,
            }
        )
    return serialised


def save_replay_buffer_checkpoint(
    base_path: Path,
    buffer: ReplayBuffer,
    episode: int,
    final_path: Optional[Path] = None,
) -> Path:
    """Persist replay buffer contents and RNG states for the given episode."""

    checkpoint_path = final_path or checkpoint_path_for_episode(base_path, episode)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "capacity": buffer.capacity,
        "length": len(buffer),
        "transitions": _serialise_transitions(buffer._buffer),  # Access internal deque for serialization
        "rng_state": collect_rng_state(),
    }

    torch.save(payload, checkpoint_path)
    return checkpoint_path


def serialise_config(config: "AIConfig") -> Dict[str, Any]:
    """Convert the AIConfig dataclass into a JSON-friendly dictionary."""

    def convert(value: Any) -> Any:
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    raw_dict = asdict(config)
    return {key: convert(val) for key, val in raw_dict.items()}


def save_training_config(config: "AIConfig", base_dir: Path) -> Path:
    """Persist training hyper-parameters once per run under the agent directory."""
    base_dir.mkdir(parents=True, exist_ok=True)
    config_path = base_dir / "config.json"
    if not config_path.exists():
        with config_path.open("w", encoding="utf-8") as fp:
            json.dump(serialise_config(config), fp, indent=2)
    return config_path


def save_episode_metrics(save_path: Path, metrics: List[dict]) -> Path:
    """Persist per-episode statistics to a CSV next to the model checkpoint."""
    metrics_path = save_path.with_name(f"{save_path.stem}_metrics.csv")
    with metrics_path.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["episode", "reward", "epsilon_start", "epsilon_end", "mean_loss"],
        )
        writer.writeheader()
        writer.writerows(metrics)
    return metrics_path

