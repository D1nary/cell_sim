"""Training entry-point for the DQN agent on the `CellSimEnv` environment."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import torch

from ..core.dqn_agent import DQNAgent
from ..metrics.plot_metrics import (
    plot_epsilon,
    plot_episode_rewards,
    plot_q_values,
    plot_td_loss,
)
from .save_io import (
    checkpoint_path_for_episode,
    final_checkpoint_path,
    save_episode_metrics,
    save_replay_buffer_checkpoint,
    save_training_config,
)
from .training_state import (
    load_training_progress,
    persist_training_progress,
    save_paused_progress,
)
from ...env import CellSimEnv

if TYPE_CHECKING:  # pragma: no cover
    from ...configs import AIConfig


def resolve_device(device_flag: str) -> torch.device:
    """Return the torch.device matching the CLI flag, defaulting to CPU."""
    if device_flag == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    if device_flag == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def seed_everything(seed: int) -> None:
    """Make the run deterministic as much as possible."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_discrete_actions(
    action_space,
    dose_bins: int,
    wait_bins: int,
) -> List[np.ndarray]:
    """Discretise the continuous action space into a finite grid for DQN."""
    dose_values = np.linspace(float(action_space.low[0]), float(action_space.high[0]), num=dose_bins)
    wait_values = np.linspace(float(action_space.low[1]), float(action_space.high[1]), num=wait_bins)
    actions: List[np.ndarray] = []
    for dose in dose_values:
        for wait in wait_values:
            actions.append(np.asarray([dose, wait], dtype=np.float32))
    return actions


def linear_epsilon(step: int, start: float, end: float, decay_steps: int) -> float:
    """Linearly anneal epsilon from start to end across decay_steps."""
    if decay_steps <= 0:
        return end
    fraction = min(1.0, step / float(decay_steps))
    return start + fraction * (end - start)


def evaluate_policy(agent: DQNAgent, env: CellSimEnv, episodes: int, max_steps: int) -> Tuple[float, float]:
    """Play episodes with greedy policy and collect stats (mean reward, success rate)."""
    rewards = []
    successes = 0
    for ep in range(episodes):
        state, _ = env.reset()
        episode_reward = 0.0
        for _ in range(max_steps):
            action_idx, action = agent.select_action(state, epsilon=0.0)
            next_state, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            state = next_state
            if terminated or truncated:
                if info.get("successful", False):
                    successes += 1
                break
        rewards.append(episode_reward)
    mean_reward = float(np.mean(rewards)) if rewards else 0.0
    success_rate = successes / max(1, episodes)
    return mean_reward, success_rate


def generate_training_plots(metrics_path: Path) -> None:
    """Render training summary plots next to the metrics CSV."""

    plot_dir = metrics_path.parent
    reward_plot = plot_dir / "reward.png"
    loss_plot = plot_dir / "loss.png"
    epsilon_plot = plot_dir / "epsilon.png"
    q_values_plot = plot_dir / "q_values.png"

    plot_episode_rewards(metrics_path, save_to=reward_plot)
    plot_td_loss(metrics_path, save_to=loss_plot)
    plot_epsilon(metrics_path, save_to=epsilon_plot)

    q_plot_saved = False
    try:
        plot_q_values(metrics_path, save_to=q_values_plot)
        q_plot_saved = True
    except ValueError:
        q_plot_saved = False

    print("Training plots saved:")
    print(f" - reward: {reward_plot}")
    print(f" - loss: {loss_plot}")
    print(f" - epsilon: {epsilon_plot}")
    if q_plot_saved and q_values_plot.exists():
        print(f" - q-values: {q_values_plot}")


def run_training(config: "AIConfig", device: torch.device) -> None:
    """Run the full DQN training loop and optional evaluation."""
    # Lock reproducible behaviour using the externally provided seed.
    seed_everything(config.seed)

    print(f"Using device: {device}")
    if device.type == "cuda":
        device_index = device.index if device.index is not None else torch.cuda.current_device()
        cuda_name = torch.cuda.get_device_name(device_index)
        print(f"CUDA device: {cuda_name}")

    env = CellSimEnv(
        max_dose=config.max_dose,
        max_wait=config.max_wait,
        min_dose=config.min_dose,
        min_wait=config.min_wait,
    )
    discrete_actions = build_discrete_actions(env.action_space, config.dose_bins, config.wait_bins)
    state_dim = int(np.prod(env.observation_space.shape))  # type: ignore

    agent = DQNAgent(state_dim, discrete_actions, device, config)
    checkpoint_base_path = config.save_agent_path / "agent" / "dqn_agent.pt"
    buffer_base_path = config.save_agent_path / "buffer" / "replay_buffer.pt"
    agent_final_path = final_checkpoint_path(checkpoint_base_path, "agent_final")
    buffer_final_path = final_checkpoint_path(buffer_base_path, "replay_buffer_final")
    paused_agent_path = final_checkpoint_path(checkpoint_base_path, "agent_paused")
    paused_buffer_path = final_checkpoint_path(buffer_base_path, "replay_buffer_paused")

    save_training_config(config, config.save_agent_path)
    checkpoint_base_path.parent.mkdir(parents=True, exist_ok=True)
    buffer_base_path.parent.mkdir(parents=True, exist_ok=True)

    progress = load_training_progress(config, agent)
    total_steps = progress.total_steps
    episode_rewards = progress.episode_rewards if progress.episode_rewards is not None else []
    losses = progress.losses if progress.losses is not None else []
    episode_metrics = progress.episode_metrics if progress.episode_metrics is not None else []
    metrics_path = progress.metrics_path
    last_checkpoint_path = progress.last_checkpoint_path
    last_buffer_path = progress.last_buffer_path
    start_episode = progress.start_episode

    current_episode = start_episode
    try:
        for episode in range(start_episode, config.episodes + 1):
            current_episode = episode

            state, _ = env.reset(seed=config.seed + episode)
            env.growth(config.growth_hours)

            episode_reward = 0.0
            info: Dict[str, object] = {}

            current_epsilon = config.epsilon_start
            episode_initial_epsilon = None
            episode_losses: List[float] = []

            for _ in range(config.max_steps):
                current_epsilon = linear_epsilon(
                    total_steps,
                    config.epsilon_start,
                    config.epsilon_end,
                    config.epsilon_decay_steps,
                )
                if episode_initial_epsilon is None:
                    episode_initial_epsilon = current_epsilon
                action_idx, action = agent.select_action(state, current_epsilon)
                next_state, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

                agent.store_transition(state, action_idx, reward, next_state, done)

                loss = agent.update()

                if loss is not None:
                    losses.append(loss)
                    episode_losses.append(loss)

                state = next_state
                episode_reward += reward
                total_steps += 1

                if done:
                    break

            if episode_initial_epsilon is None:
                episode_initial_epsilon = current_epsilon
            episode_final_epsilon = current_epsilon
            avg_episode_loss = float(np.mean(episode_losses)) if episode_losses else math.nan

            episode_metrics.append(
                {
                    "episode": episode,
                    "reward": episode_reward,
                    "epsilon_start": episode_initial_epsilon,
                    "epsilon_end": episode_final_epsilon,
                    "mean_loss": avg_episode_loss,
                }
            )

            episode_rewards.append(episode_reward)
            info_str = "success" if info.get("successful", False) else "timeout" if info.get("timeout", False) else "failure"
            avg_reward = np.mean(episode_rewards[-10:])
            avg_loss = np.mean(losses[-10:]) if losses else math.nan

            print(
                f"Episode {episode:04d} | steps: {total_steps:06d} | reward: {episode_reward:.3f} | "
                f"avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | eps: {current_epsilon:.3f} | {info_str}"
            )

            if config.save_episodes > 0 and (episode % config.save_episodes == 0 or episode == config.episodes):
                is_final_episode = episode == config.episodes
                checkpoint_path = (
                    agent_final_path if is_final_episode else checkpoint_path_for_episode(checkpoint_base_path, episode)
                )
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                agent.save(str(checkpoint_path))
                buffer_path = save_replay_buffer_checkpoint(
                    buffer_base_path,
                    agent.replay_buffer,
                    episode,
                    final_path=buffer_final_path if is_final_episode else None,
                )
                metrics_path = save_episode_metrics(checkpoint_path, episode_metrics)
                last_checkpoint_path = checkpoint_path
                last_buffer_path = buffer_path
                persist_training_progress(
                    config,
                    episode + 1,
                    total_steps,
                    episode_rewards,
                    losses,
                    episode_metrics,
                    checkpoint_path,
                    buffer_path,
                    metrics_path,
                    "running",
                )
                print(
                    "Checkpoint saved at episode "
                    f"{episode} -> model: {checkpoint_path}, buffer: {buffer_path}, metrics: {metrics_path}"
                )

        if metrics_path is None:
            final_episode = config.episodes if config.episodes > 0 else 0
            checkpoint_path = agent_final_path
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            agent.save(str(checkpoint_path))
            buffer_path = save_replay_buffer_checkpoint(
                buffer_base_path,
                agent.replay_buffer,
                final_episode,
                final_path=buffer_final_path,
            )
            metrics_path = save_episode_metrics(checkpoint_path, episode_metrics)
            last_checkpoint_path = checkpoint_path
            last_buffer_path = buffer_path
            persist_training_progress(
                config,
                config.episodes + 1,
                total_steps,
                episode_rewards,
                losses,
                episode_metrics,
                checkpoint_path,
                buffer_path,
                metrics_path,
                "running",
            )
            print(f"Model saved to {checkpoint_path}")
            print(f"Replay buffer saved to {buffer_path}")
            print(f"Episode metrics saved to {metrics_path}")

        if config.eval_episodes > 0:
            mean_reward, success_rate = evaluate_policy(agent, env, config.eval_episodes, config.max_steps)
            print(
                f"Final evaluation -> mean reward: {mean_reward:.3f}, success rate: {success_rate:.2%}"
            )

        if metrics_path is not None:
            try:
                generate_training_plots(metrics_path)
            except Exception as plot_error:  # pragma: no cover - best-effort plotting
                print(f"Failed to generate training plots: {plot_error}")

        if last_checkpoint_path is not None and last_buffer_path is not None:
            persist_training_progress(
                config,
                config.episodes + 1,
                total_steps,
                episode_rewards,
                losses,
                episode_metrics,
                last_checkpoint_path,
                last_buffer_path,
                metrics_path,
                "completed",
            )
    
    except KeyboardInterrupt:
        print("\nTraining interrupted by user. Saving pause checkpoint...")
        checkpoint_path, buffer_path = save_paused_progress(
            config,
            agent,
            buffer_base_path,
            paused_agent_path,
            paused_buffer_path,
            current_episode,
            total_steps,
            episode_rewards,
            losses,
            episode_metrics,
            metrics_path,
        )
        last_checkpoint_path = checkpoint_path
        last_buffer_path = buffer_path
        print(f"Training paused at episode {current_episode}. Checkpoints saved to {checkpoint_path}")
    finally:
        env.close()
