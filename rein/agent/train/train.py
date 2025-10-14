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


class RewardAwareEpsilonController:
    """Dynamically modulate ε-greedy exploration based on reward trends."""

    def __init__(
        self,
        epsilon_start: float,
        epsilon_end: float,
        base_decay_steps: int,
        patience: int,
        min_delta_floor: float,
        min_delta_relative: float,
        epsilon_multiplier_bounds: Tuple[float, float],
        decay_multiplier_bounds: Tuple[float, float],
        epsilon_plateau_factor: float,
        epsilon_improve_factor: float,
        decay_plateau_factor: float,
        decay_improve_factor: float,
        epsilon_max_bump_factor: float,
    ) -> None:
        self.epsilon_start = float(epsilon_start)
        self.epsilon_end = float(epsilon_end)
        self.base_decay_steps = max(1, int(base_decay_steps))
        self.patience = max(1, int(patience))
        self.min_delta_floor = float(min_delta_floor)
        self.min_delta_relative = float(min_delta_relative)

        self.best_score = -math.inf
        self.episodes_since_improvement = 0

        self.epsilon_multiplier = 1.0
        self.decay_multiplier = 1.0

        self.epsilon_multiplier_bounds = tuple(map(float, epsilon_multiplier_bounds))
        self.decay_multiplier_bounds = tuple(map(float, decay_multiplier_bounds))

        self.epsilon_plateau_factor = float(epsilon_plateau_factor)
        self.epsilon_improve_factor = float(epsilon_improve_factor)

        self.decay_plateau_factor = float(decay_plateau_factor)
        self.decay_improve_factor = float(decay_improve_factor)

        self.epsilon_max_bump = self.epsilon_start * float(epsilon_max_bump_factor)

    @property
    def effective_decay_steps(self) -> int:
        """Return the current decay horizon incorporating reward-aware scaling."""
        scaled = int(self.base_decay_steps * self.decay_multiplier)
        return max(1, scaled)

    def value(self, step: int) -> float:
        """Compute the exploration rate for the given global step."""
        base = linear_epsilon(step, self.epsilon_start, self.epsilon_end, self.effective_decay_steps)
        scaled = self.epsilon_multiplier * base
        return float(np.clip(scaled, self.epsilon_end, self.epsilon_max_bump))

    def update(self, score: float) -> Optional[Dict[str, float]]:
        """Update internal multipliers from the latest reward statistic."""
        if not math.isfinite(score):
            # Skip non-finite rewards to avoid contaminating the schedule.
            return None

        if self.best_score == -math.inf:
            # Seed the baseline once a valid score appears.
            self.best_score = score
            self.episodes_since_improvement = 0
            return None

        adjusted = None
        delta_threshold = max(self.min_delta_floor, self.min_delta_relative * abs(self.best_score))
        if score > self.best_score + delta_threshold:
            # Reward improved: tighten multipliers to focus on exploitation.
            self.best_score = score
            self.episodes_since_improvement = 0
            old_multiplier = self.epsilon_multiplier
            self.epsilon_multiplier = max(
                self.epsilon_multiplier * self.epsilon_improve_factor,
                self.epsilon_multiplier_bounds[0],
            )
            old_decay = self.decay_multiplier
            self.decay_multiplier = max(
                self.decay_multiplier * self.decay_improve_factor,
                self.decay_multiplier_bounds[0],
            )
            adjusted = {
                "reason": "improved",
                "epsilon_multiplier": self.epsilon_multiplier,
                "decay_multiplier": self.decay_multiplier,
                "prev_epsilon_multiplier": old_multiplier,
                "prev_decay_multiplier": old_decay,
            }
        else:
            self.episodes_since_improvement += 1
            if self.episodes_since_improvement >= self.patience:
                # Reward plateau: loosen multipliers to encourage exploration.
                self.episodes_since_improvement = 0
                old_multiplier = self.epsilon_multiplier
                self.epsilon_multiplier = min(
                    self.epsilon_multiplier * self.epsilon_plateau_factor,
                    self.epsilon_multiplier_bounds[1],
                )
                old_decay = self.decay_multiplier
                self.decay_multiplier = min(
                    self.decay_multiplier * self.decay_plateau_factor,
                    self.decay_multiplier_bounds[1],
                )
                adjusted = {
                    "reason": "plateau",
                    "epsilon_multiplier": self.epsilon_multiplier,
                    "decay_multiplier": self.decay_multiplier,
                    "prev_epsilon_multiplier": old_multiplier,
                    "prev_decay_multiplier": old_decay,
                }
        if adjusted is not None:
            adjusted["effective_decay_steps"] = int(self.effective_decay_steps)
        return adjusted


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

    # Print using device
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

    # Build the discrete action catalogue required by the DQN head.
    discrete_actions = build_discrete_actions(env.action_space, config.dose_bins, config.wait_bins)
    state_dim = int(np.prod(env.observation_space.shape))  # type: ignore

    # Assemble agent and checkpoint bookkeeping paths.
    agent = DQNAgent(state_dim, discrete_actions, device, config)
    checkpoint_base_path = config.save_agent_path / "agent" / "dqn_agent.pt"
    buffer_base_path = config.save_agent_path / "buffer" / "replay_buffer.pt"
    agent_final_path = final_checkpoint_path(checkpoint_base_path, "agent_final")
    buffer_final_path = final_checkpoint_path(buffer_base_path, "replay_buffer_final")
    paused_agent_path = final_checkpoint_path(checkpoint_base_path, "agent_paused")
    paused_buffer_path = final_checkpoint_path(buffer_base_path, "replay_buffer_paused")
    epsilon_log_dir = config.save_agent_path.parent / "epsilon_controller"
    epsilon_log_dir.mkdir(parents=True, exist_ok=True)
    epsilon_log_path = epsilon_log_dir / "adjustments.csv"
    if not epsilon_log_path.exists():
        with epsilon_log_path.open("w", encoding="utf-8") as log_fp:
            log_fp.write(
                "episode,total_steps,reason,epsilon_multiplier,decay_multiplier,epsilon_current,effective_decay_steps\n"
            )

    # Store hyperparameters next to artifacts to keep the run reproducible.
    save_training_config(config, config.save_agent_path)
    checkpoint_base_path.parent.mkdir(parents=True, exist_ok=True)
    buffer_base_path.parent.mkdir(parents=True, exist_ok=True)

    # Restore persisted progress (if there are) so runs can resume seamlessly.
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
    epsilon_controller = RewardAwareEpsilonController(
        config.epsilon_start,
        config.epsilon_end,
        config.epsilon_decay_steps,
        config.reward_patience,
        config.reward_min_delta_floor,
        config.reward_min_delta_relative,
        config.reward_epsilon_multiplier_bounds,
        config.reward_decay_multiplier_bounds,
        config.reward_epsilon_plateau_factor,
        config.reward_epsilon_improve_factor,
        config.reward_decay_plateau_factor,
        config.reward_decay_improve_factor,
        config.reward_epsilon_max_bump_factor,
    )
    try:
        for episode in range(start_episode, config.episodes + 1):
            current_episode = episode

            # Reset environment with deterministic seed and apply initial growth phase.
            state, _ = env.reset(seed=config.seed + episode)
            env.growth(config.growth_hours)

            episode_reward = 0.0
            info: Dict[str, object] = {}

            episode_initial_epsilon = None
            episode_losses: List[float] = []

            for _ in range(config.max_steps):
                
                # Decay exploration rate and sample an action from the agent policy.
                # The reward-aware controller stretches/shrinks epsilon in response to performance trends.
                current_epsilon = epsilon_controller.value(total_steps)
                if episode_initial_epsilon is None:
                    episode_initial_epsilon = current_epsilon
                action_idx, action = agent.select_action(state, current_epsilon)
                next_state, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

                # Push transition to replay buffer and trigger a learning step.
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

            # Log the episode reward, outcome status, and rolling 10-episode reward/loss averages.
            episode_rewards.append(episode_reward)
            info_str = "success" if info.get("successful", False) else "timeout" if info.get("timeout", False) else "failure"
            avg_reward = float(np.mean(episode_rewards[-10:]))
            avg_loss = np.mean(losses[-10:]) if losses else math.nan
            
            # Adapt the optimizer learning rate whenever the recent reward stalls or declines.
            previous_lr = float(agent.optimizer.param_groups[0]["lr"])
            current_lr = agent.step_reward_scheduler(avg_reward)
            lr_reduced = current_lr < (previous_lr - 1e-12)
            
            # Feed the smoothed reward back into the epsilon controller to retune exploration pressure.
            reward_adjustment = epsilon_controller.update(avg_reward)

            print(
                f"Episode {episode:04d} | steps: {total_steps:06d} | reward: {episode_reward:.3f} | "
                f"avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | lr: {current_lr:.6f} | "
                f"eps: {current_epsilon:.3f} | {info_str}"
            )

            if lr_reduced:
                print(
                    f"    Learning rate reduced from {previous_lr:.6f} to {current_lr:.6f} after reward plateau/decrease."
                )
                
            if reward_adjustment is not None:
                reason = reward_adjustment.get("reason", "plateau")
                prev_eps_mult = reward_adjustment.get("prev_epsilon_multiplier", 1.0)
                new_eps_mult = reward_adjustment.get("epsilon_multiplier", prev_eps_mult)
                prev_decay = reward_adjustment.get("prev_decay_multiplier", 1.0)
                new_decay = reward_adjustment.get("decay_multiplier", prev_decay)
                effective_steps = int(reward_adjustment.get("effective_decay_steps", epsilon_controller.effective_decay_steps))
                print(
                    f"    Reward-aware epsilon update ({reason}) -> "
                    f"eps-mult: {prev_eps_mult:.3f} -> {new_eps_mult:.3f}, "
                    f"decay-mult: {prev_decay:.3f} -> {new_decay:.3f}, "
                    f"effective decay steps: {effective_steps}, "
                    f"epsilon current: {current_epsilon:.3f}"
                )
                with epsilon_log_path.open("a", encoding="utf-8") as log_fp:
                    log_fp.write(
                        f"{episode},{total_steps},{reason},{new_eps_mult:.6f},{new_decay:.6f},{current_epsilon:.6f},{effective_steps}\n"
                    )

            if config.save_episodes > 0 and (episode % config.save_episodes == 0 or episode == config.episodes):
                # Periodically persist model, replay buffer, and metrics to disk.
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
            # Guarantee at least one final checkpoint even if periodic saves were disabled.
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
            # Optionally evaluate the greedy policy after training completes.
            mean_reward, success_rate = evaluate_policy(agent, env, config.eval_episodes, config.max_steps)
            print(
                f"Final evaluation -> mean reward: {mean_reward:.3f}, success rate: {success_rate:.2%}"
            )

        if metrics_path is not None:
            try:
                # Generate visual summaries to help inspect training dynamics.
                generate_training_plots(metrics_path)
            except Exception as plot_error:  # pragma: no cover - best-effort plotting
                print(f"Failed to generate training plots: {plot_error}")

        if last_checkpoint_path is not None and last_buffer_path is not None:
            # Mark the run as completed so future invocations avoid resuming incorrectly.
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
            # Persist a pause checkpoint so the user can resume later.
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
        # Clean up the environment explicitly to release resources.
        env.close()
