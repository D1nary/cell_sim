"""Helpers for persisting and restoring training progress."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, TYPE_CHECKING

from .save_io import (
    load_replay_buffer_checkpoint,
    load_training_state,
    restore_rng_state,
    save_replay_buffer_checkpoint,
    save_training_state,
)

if TYPE_CHECKING:  # pragma: no cover
    from ..core.dqn_agent import DQNAgent
    from ...configs import AIConfig


@dataclass
class TrainingProgress:
    """Container describing the current persisted training progress."""

    start_episode: int = 1
    total_steps: int = 0
    episode_rewards: List[float] | None = None
    losses: List[float] | None = None
    episode_metrics: List[dict] | None = None
    metrics_path: Optional[Path] = None
    last_checkpoint_path: Optional[Path] = None
    last_buffer_path: Optional[Path] = None

    def ensure_lists(self) -> None:
        """Materialise list attributes that may still be None."""
        if self.episode_rewards is None:
            self.episode_rewards = []
        if self.losses is None:
            self.losses = []
        if self.episode_metrics is None:
            self.episode_metrics = []


def load_training_progress(config: "AIConfig", agent: "DQNAgent") -> TrainingProgress:
    """Load persisted training progress and restore model/buffer if requested."""
    progress = TrainingProgress()
    progress.ensure_lists()

    if not getattr(config, "resume", False):
        return progress

    resume_dir = (config.resume_from or config.save_agent_path).resolve()
    try:
        resume_state = load_training_state(resume_dir)
    except FileNotFoundError:
        print(f"No training state found in {resume_dir}; starting fresh.")
        return progress

    agent_checkpoint_value = resume_state.get("agent_checkpoint")
    if agent_checkpoint_value:
        agent_checkpoint = Path(agent_checkpoint_value)
        if not agent_checkpoint.is_absolute():
            agent_checkpoint = resume_dir / agent_checkpoint
        if agent_checkpoint.exists():
            agent.load(str(agent_checkpoint))
            progress.last_checkpoint_path = agent_checkpoint
            print(f"Resumed agent from {agent_checkpoint}")
        else:
            print(f"Agent checkpoint not found at {agent_checkpoint}; using initialised weights.")

    buffer_checkpoint_value = resume_state.get("buffer_checkpoint")
    rng_state = None
    if buffer_checkpoint_value:
        buffer_checkpoint = Path(buffer_checkpoint_value)
        if not buffer_checkpoint.is_absolute():
            buffer_checkpoint = resume_dir / buffer_checkpoint
        if buffer_checkpoint.exists():
            replay_buffer, rng_state = load_replay_buffer_checkpoint(
                buffer_checkpoint,
                agent.replay_buffer.capacity,
            )
            agent.replay_buffer = replay_buffer
            progress.last_buffer_path = buffer_checkpoint
            print(f"Resumed replay buffer from {buffer_checkpoint}")
        else:
            print(f"Replay buffer checkpoint not found at {buffer_checkpoint}; starting empty buffer.")
    restore_rng_state(rng_state)

    progress.total_steps = int(resume_state.get("total_steps", 0))
    progress.episode_rewards = list(resume_state.get("episode_rewards", []))
    progress.losses = list(resume_state.get("losses", []))
    progress.episode_metrics = list(resume_state.get("episode_metrics", []))
    metrics_value = resume_state.get("metrics_path")
    if metrics_value:
        metrics_candidate = Path(metrics_value)
        if not metrics_candidate.is_absolute():
            metrics_candidate = resume_dir / metrics_candidate
        progress.metrics_path = metrics_candidate
    progress.start_episode = max(1, int(resume_state.get("next_episode", 1)))

    status = resume_state.get("status")
    if status:
        print(f"Resuming from state marked as '{status}'.")
    if progress.start_episode > config.episodes:
        print("All configured episodes already completed; skipping training loop.")

    progress.ensure_lists()
    return progress


def persist_training_progress(
    config: "AIConfig",
    next_episode: int,
    total_steps: int,
    episode_rewards: List[float],
    losses: List[float],
    episode_metrics: List[dict],
    checkpoint_path: Path,
    buffer_path: Path,
    metrics: Optional[Path],
    status: str,
) -> None:
    """Persist metadata required to resume training later."""
    metrics_value = str(metrics.resolve()) if metrics is not None else None
    save_training_state(
        config.save_agent_path,
        {
            "next_episode": next_episode,
            "total_steps": total_steps,
            "episode_rewards": episode_rewards,
            "losses": losses,
            "episode_metrics": episode_metrics,
            "agent_checkpoint": str(checkpoint_path.resolve()),
            "buffer_checkpoint": str(buffer_path.resolve()),
            "metrics_path": metrics_value,
            "status": status,
        },
    )


def save_paused_progress(
    config: "AIConfig",
    agent: "DQNAgent",
    buffer_base_path: Path,
    paused_agent_path: Path,
    paused_buffer_path: Path,
    current_episode: int,
    total_steps: int,
    episode_rewards: List[float],
    losses: List[float],
    episode_metrics: List[dict],
    metrics_path: Optional[Path],
) -> Tuple[Path, Path]:
    """Save agent, buffer and metadata when training is paused/interrupted."""
    paused_agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(paused_agent_path))
    buffer_path = save_replay_buffer_checkpoint(
        buffer_base_path,
        agent.replay_buffer,
        current_episode,
        final_path=paused_buffer_path,
    )
    persist_training_progress(
        config,
        current_episode,
        total_steps,
        episode_rewards,
        losses,
        episode_metrics,
        paused_agent_path,
        buffer_path,
        metrics_path,
        "paused",
    )
    return paused_agent_path, buffer_path
