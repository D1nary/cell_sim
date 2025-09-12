"""Utility helpers for training and evaluation scripts."""
from __future__ import annotations

import json
import os
import random
from dataclasses import is_dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def seed_everything(seed: int) -> None:
    """Seed Python, NumPy, and best-effort the C++ sim RNG."""
    random.seed(seed)
    np.random.seed(seed)
    # Best-effort seed of the C++ RNG (module is optional at import time)
    try:
        import cell_sim  # type: ignore

        cell_sim.seed(int(seed) & 0xFFFFFFFF)
    except Exception:
        pass


def make_run_dir(base: Path, run_name: str) -> Path:
    """Create a timestamped run directory under ``base`` using ``run_name``."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = base / f"{ts}_{run_name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_json(path: Path, data: Any) -> None:
    """Save Python data as JSON with nice formatting."""
    if is_dataclass(data):
        data = asdict(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def maybe_env_var(name: str, default: Optional[str] = None) -> str:
    """Read an environment variable with a default."""
    v = os.getenv(name)
    return v if v is not None else (default or "")


__all__ = [
    "seed_everything",
    "make_run_dir",
    "save_json",
    "maybe_env_var",
]

