"""Plotting utilities for DQN training metrics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from numpy.typing import ArrayLike

__all__ = [
    "EpisodeMetrics",
    "read_episode_metrics",
    "plot_episode_rewards",
    "plot_td_loss",
    "plot_epsilon",
    "plot_q_values",
]


@dataclass(frozen=True)
class EpisodeMetrics:
    """Container for per-episode statistics captured during training."""

    episode: int
    reward: float
    epsilon_start: Optional[float]
    epsilon_end: Optional[float]
    mean_loss: Optional[float]
    q_mean: Optional[float]
    q_max: Optional[float]


def _to_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "" or stripped.lower() == "nan":
        return None
    return float(stripped)


def read_episode_metrics(metrics_path: Path | str) -> List[EpisodeMetrics]:
    """Load the CSV file produced by ``save_episode_metrics`` into structured entries."""

    path = Path(metrics_path)
    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")

    with path.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"episode", "reward"}
        if not required.issubset(reader.fieldnames or {}):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"Metrics file {path} missing columns: {missing}")
        q_mean_keys = ("q_mean", "q_value_mean", "mean_q_value", "mean_q")
        q_max_keys = ("q_max", "q_value_max", "max_q_value")
        records: List[EpisodeMetrics] = []
        for row in reader:
            episode = int(row["episode"])
            reward = float(row["reward"])
            epsilon_start = _to_float(row.get("epsilon_start"))
            epsilon_end = _to_float(row.get("epsilon_end"))
            mean_loss = _to_float(row.get("mean_loss"))
            q_mean = None
            for key in q_mean_keys:
                if key in row:
                    q_mean = _to_float(row.get(key))
                    if q_mean is not None:
                        break
            q_max = None
            for key in q_max_keys:
                if key in row:
                    q_max = _to_float(row.get(key))
                    if q_max is not None:
                        break
            records.append(
                EpisodeMetrics(
                    episode=episode,
                    reward=reward,
                    epsilon_start=epsilon_start,
                    epsilon_end=epsilon_end,
                    mean_loss=mean_loss,
                    q_mean=q_mean,
                    q_max=q_max,
                )
            )
    records.sort(key=lambda entry: entry.episode)
    return records


def _moving_average(values: ArrayLike, window: int) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    if data.size == 0:
        return np.array([])
    if window <= 1:
        return data.copy()
    window = min(window, data.size)
    result = np.full(data.shape, np.nan)
    valid_mask = ~np.isnan(data)
    cumulative = np.cumsum(np.where(valid_mask, data, 0.0))
    counts = np.cumsum(valid_mask.astype(np.int64))
    for idx in range(window - 1, data.size):
        total = cumulative[idx] - (cumulative[idx - window] if idx >= window else 0.0)
        count = counts[idx] - (counts[idx - window] if idx >= window else 0)
        if count > 0:
            result[idx] = total / count
    return result


def plot_episode_rewards(
    metrics_path: Path | str,
    *,
    window: int = 50,
    save_to: Path | str | None = None,
) -> Figure:
    """Plot per-episode rewards together with a moving average trend."""

    metrics = read_episode_metrics(metrics_path)
    episodes = [entry.episode for entry in metrics]
    rewards = np.asarray([entry.reward for entry in metrics], dtype=float)

    fig, ax = plt.subplots()
    ax.plot(episodes, rewards, label="Reward", color="tab:blue", linewidth=1.0)
    if rewards.size and window > 1:
        trend = _moving_average(rewards, window)
        ax.plot(episodes, trend, label=f"Moving avg ({window})", color="tab:orange", linewidth=1.5)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Reward")
    ax.set_title("Episode reward")
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout()

    if save_to is not None:
        fig.savefig(Path(save_to), bbox_inches="tight")
    return fig


def plot_td_loss(
    metrics_path: Path | str,
    *,
    loss_history_path: Path | str | None = None,
    window: int = 200,
    save_to: Path | str | None = None,
) -> Figure:
    """Plot TD loss per update (or episode) with an optional moving average."""

    updates: np.ndarray
    losses: np.ndarray

    if loss_history_path is not None:
        path = Path(loss_history_path)
        if not path.exists():
            raise FileNotFoundError(f"Loss history file not found: {path}")
        with path.open("r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise ValueError(f"Loss history file {path} missing header")
            loss_key = None
            for candidate in ("loss", "td_loss", "value"):
                if candidate in reader.fieldnames:
                    loss_key = candidate
                    break
            if loss_key is None:
                raise ValueError(f"Loss history file {path} missing loss column")
            step_key = None
            for candidate in ("update", "step", "iteration", "episode"):
                if candidate in reader.fieldnames:
                    step_key = candidate
                    break
            if step_key is None:
                step_key = "index"
            step_values: List[int] = []
            raw_losses: List[float] = []
            for idx, row in enumerate(reader):
                value = _to_float(row.get(loss_key))
                if value is None:
                    continue
                raw_losses.append(value)
                if step_key == "index":
                    step_values.append(idx)
                else:
                    step_values.append(int(float(row.get(step_key, idx))))
        updates = np.asarray(step_values, dtype=int)
        losses = np.asarray(raw_losses, dtype=float)
    else:
        metrics = read_episode_metrics(metrics_path)
        updates = np.asarray([entry.episode for entry in metrics], dtype=int)
        loss_values: List[Optional[float]] = [entry.mean_loss for entry in metrics]
        filtered = [(step, loss) for step, loss in zip(updates, loss_values) if loss is not None and not np.isnan(loss)]
        if not filtered:
            raise ValueError("No loss values available in metrics; provide loss_history_path")
        updates = np.asarray([step for step, _ in filtered], dtype=int)
        losses = np.asarray([loss for _, loss in filtered], dtype=float)

    fig, ax = plt.subplots()
    ax.plot(updates, losses, label="TD loss", color="tab:red", linewidth=0.9)
    if losses.size and window > 1:
        trend = _moving_average(losses, window)
        ax.plot(updates, trend, label=f"Moving avg ({window})", color="tab:purple", linewidth=1.5)
    ax.set_xlabel("Update" if loss_history_path is not None else "Episode")
    ax.set_ylabel("Loss")
    ax.set_title("Temporal-difference loss")
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout()

    if save_to is not None:
        fig.savefig(Path(save_to), bbox_inches="tight")
    return fig


def plot_epsilon(
    metrics_path: Path | str,
    *,
    save_to: Path | str | None = None,
) -> Figure:
    """Plot epsilon scheduling per episode using the stored metrics."""

    metrics = read_episode_metrics(metrics_path)
    episodes = np.asarray([entry.episode for entry in metrics], dtype=int)
    eps_start = np.asarray([entry.epsilon_start for entry in metrics], dtype=float)
    eps_end = np.asarray([entry.epsilon_end for entry in metrics], dtype=float)

    fig, ax = plt.subplots()
    if np.isfinite(eps_start).any():
        ax.plot(episodes, eps_start, label="Epsilon start", color="tab:green", linewidth=1.0)
    if np.isfinite(eps_end).any():
        ax.plot(episodes, eps_end, label="Epsilon end", color="tab:gray", linewidth=1.0)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Epsilon")
    ax.set_title("Exploration rate")
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout()

    if save_to is not None:
        fig.savefig(Path(save_to), bbox_inches="tight")
    return fig


def plot_q_values(
    metrics_path: Path | str,
    *,
    window: int = 1,
    save_to: Path | str | None = None,
) -> Figure:
    """Plot mean and maximum Q-values per episode for the selected actions."""

    metrics = read_episode_metrics(metrics_path)
    episodes = np.asarray([entry.episode for entry in metrics], dtype=int)
    q_mean = np.asarray([entry.q_mean for entry in metrics], dtype=float)
    q_max = np.asarray([entry.q_max for entry in metrics], dtype=float)

    if not np.isfinite(q_mean).any() or not np.isfinite(q_max).any():
        raise ValueError(
            "Metrics file does not contain Q-value statistics; ensure training stores q_mean and q_max"
        )

    fig, ax = plt.subplots()
    ax.plot(episodes, q_mean, label="Mean Q", color="tab:blue", linewidth=1.0)
    ax.plot(episodes, q_max, label="Max Q", color="tab:orange", linewidth=1.0)

    if window > 1:
        mean_trend = _moving_average(q_mean, window)
        max_trend = _moving_average(q_max, window)
        ax.plot(episodes, mean_trend, label=f"Mean Q avg ({window})", color="tab:blue", linewidth=1.8, alpha=0.6)
        ax.plot(episodes, max_trend, label=f"Max Q avg ({window})", color="tab:orange", linewidth=1.8, alpha=0.6)

    ax.set_xlabel("Episode")
    ax.set_ylabel("Q-value")
    ax.set_title("Q-values of selected actions")
    ax.legend()
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout()

    if save_to is not None:
        fig.savefig(Path(save_to), bbox_inches="tight")
    return fig
