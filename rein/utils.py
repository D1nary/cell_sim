from __future__ import annotations

import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import torch


def select_device(preference: str = "auto") -> torch.device:
    """Choose the compute device honoring the preference string."""
    pref = (preference or "cpu").lower()
    if pref == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    if pref == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if pref == "mps" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_seed(seed: int) -> None:
    """Seed python, numpy and torch RNGs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def schedule_linear(start: float, end: float, progress: float) -> float:
    """Linear schedule helper clipping the progress inside [0, 1]."""
    p = float(np.clip(progress, 0.0, 1.0))
    return start + p * (end - start)


def ensure_dir(path: Path | str) -> Path:
    """Create directory (if needed) and return it as Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def format_metrics(metrics: dict[str, float]) -> str:
    """Return a pretty string for scalar metrics."""
    parts: list[str] = []
    for key, value in metrics.items():
        parts.append(f"{key}={value:.4f}")
    return " | ".join(parts)


def timestamp() -> str:
    """Return a compact UTC timestamp."""
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def to_tensor(data: Iterable[float], device: torch.device) -> torch.Tensor:
    """Convert iterable to float32 tensor on device."""
    return torch.as_tensor(list(data), dtype=torch.float32, device=device)


__all__ = [
    "ensure_dir",
    "format_metrics",
    "schedule_linear",
    "select_device",
    "set_seed",
    "timestamp",
    "to_tensor",
]
