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
    plot_learning_rate,
    plot_q_values,
    plot_td_loss,
)
from .save_io import (
    checkpoint_path_for_episode,
    final_checkpoint_path,
    append_episode_metrics,
    save_replay_buffer_checkpoint,
    save_training_config,
)
from .training_state import (
    load_training_progress,
    persist_training_progress,
    save_paused_progress,
)
from ...env import CellSimEnv
from ...configs.defaults import DEFAULT_CONFIG

if TYPE_CHECKING:  # pragma: no cover
    from ...configs import AIConfig


CHECKPOINT_INTERVAL = 10
METRICS_LOG_NAME = "training_log.csv"


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
    
    # Linearly blend start and end according to normalized decay progress.
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
        epsilon_multiplier: float = DEFAULT_CONFIG.reward_epsilon_multiplier,
        decay_multiplier: float = DEFAULT_CONFIG.reward_decay_multiplier,
    ) -> None:
        

        self.epsilon_start = float(epsilon_start)
        self.epsilon_end = float(epsilon_end)
        self.base_decay_steps = max(1, int(base_decay_steps))
        self.patience = max(1, int(patience))
        self.min_delta_floor = float(min_delta_floor)
        self.min_delta_relative = float(min_delta_relative)

        self.best_score = -math.inf
        self.episodes_since_improvement = 0

        self.epsilon_multiplier = float(epsilon_multiplier)
        self.decay_multiplier = float(decay_multiplier)
 
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
        # Score is the awerage reward
        if not math.isfinite(score):
            # Skip non-finite rewards to avoid contaminating the schedule.
            return None

        # Seed the baseline once a valid score appears.
        if self.best_score == -math.inf:
            self.best_score = score
            self.episodes_since_improvement = 0
            return None

        adjusted = None
        delta_threshold = max(self.min_delta_floor, self.min_delta_relative * abs(self.best_score))
        # Reward improved: Less exploration reducing multipliers
        if score > self.best_score + delta_threshold:
            self.best_score = score
            self.episodes_since_improvement = 0
            old_multiplier = self.epsilon_multiplier
            
            # Reduce epsilon_multiplier
            self.epsilon_multiplier = max(
                self.epsilon_multiplier * self.epsilon_improve_factor,
                self.epsilon_multiplier_bounds[0],
            )
            old_decay = self.decay_multiplier
            
            # Reduce decay multiplier
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

        # Plateu (reward not improving): Focus on exploration incrising multipliers
        else:
            self.episodes_since_improvement += 1
            if self.episodes_since_improvement >= self.patience:
                # Reward plateau: loosen multipliers to encourage exploration.
                self.episodes_since_improvement = 0
                old_multiplier = self.epsilon_multiplier

                # Increment epsilon_multiplier
                self.epsilon_multiplier = min(
                    self.epsilon_multiplier * self.epsilon_plateau_factor,
                    self.epsilon_multiplier_bounds[1],
                )
                old_decay = self.decay_multiplier

                # Increment decay multiplier
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
        # If the dictionary exists (meaning epsilon and its decay have been adjusted)
        # add the extra detail (effective_decay_steps)
        if adjusted is not None:
            # effective_decay_steps is passed to the linear decay function
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
    learning_rate_plot = plot_dir / "learning_rate.png"

    plot_episode_rewards(metrics_path, save_to=reward_plot)
    plot_td_loss(metrics_path, save_to=loss_plot)
    plot_epsilon(metrics_path, save_to=epsilon_plot)

    lr_plot_saved = False
    try:
        plot_learning_rate(metrics_path, save_to=learning_rate_plot)
        lr_plot_saved = True
    except ValueError:
        lr_plot_saved = FalseDQNAgent

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
    if lr_plot_saved and learning_rate_plot.exists():
        print(f" - learning-rate: {learning_rate_plot}")
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

    # Iniztialize the enviroment
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
    checkpoint_base_path = config.save_agent_path / "checkpoints" / "agent" / "agent_checkpoint.pt"
    buffer_base_path = config.save_agent_path / "checkpoints" / "replay_buffer" / "replay_buffer_checkpoint.pt"
    agent_final_path = final_checkpoint_path(checkpoint_base_path, "agent_final")
    buffer_final_path = final_checkpoint_path(buffer_base_path, "replay_buffer_final")
    paused_agent_path = final_checkpoint_path(checkpoint_base_path, "agent_paused")
    paused_buffer_path = final_checkpoint_path(buffer_base_path, "replay_buffer_paused")
    use_reward_aware = bool(
        getattr(config, "reward_aware_activator", DEFAULT_CONFIG.reward_aware_activator)
    )
    epsilon_log_path: Path | None = None
    if use_reward_aware:
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
    if getattr(config, "resume", False):
        metrics_log_path = progress.metrics_path or (config.save_agent_path / METRICS_LOG_NAME)
    else:
        metrics_log_path = config.save_agent_path / METRICS_LOG_NAME
        if metrics_log_path.exists():
            metrics_log_path.unlink()
    metrics_path: Optional[Path] = metrics_log_path if metrics_log_path.exists() else None
    last_checkpoint_path = progress.last_checkpoint_path
    last_buffer_path = progress.last_buffer_path
    start_episode = progress.start_episode

    # Beginning episode
    current_episode = start_episode
    
    # Create reward aware object
    epsilon_controller: RewardAwareEpsilonController | None = None
    if use_reward_aware:
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
            epsilon_multiplier=config.reward_epsilon_multiplier,
            decay_multiplier=config.reward_decay_multiplier,
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
            episode_step_count = 0
            updates_this_episode = 0

            # Beginning steps
            for _ in range(config.max_steps):

                # Decay exploration rate and sample an action from the agent policy.
                if use_reward_aware and epsilon_controller is not None:
                    # Reward-aware controller stretches/shrinks epsilon in response to performance trends.
                    current_epsilon = epsilon_controller.value(total_steps)
                else:
                    current_epsilon = linear_epsilon(
                        total_steps,
                        config.epsilon_start,
                        config.epsilon_end,
                        config.epsilon_decay_steps,
                    )
                if episode_initial_epsilon is None:
                    episode_initial_epsilon = current_epsilon

                
                # Select action
                action_idx, action = agent.select_action(state, current_epsilon)
                
                # Step the enviroment
                next_state, reward, terminated, truncated, info = env.step(action)
                
                # Check if done or truncated
                done = terminated or truncated

                # Push transition to replay buffer and trigger a learning step.
                agent.store_transition(state, action_idx, reward, next_state, done)

                # If replay buffer has enough samples, fetch a mini-batch, calculate Huber loss
                # between current Q and target, updates policy network (backpropagation) and 
                # periodically synchronizes the target network
                loss = agent.update()

                # Store loss and episode loss
                if loss is not None:
                    losses.append(loss)
                    episode_losses.append(loss)
                    updates_this_episode += 1

                # Update state, reward counter and total step counter
                state = next_state
                episode_reward += reward
                total_steps += 1
                episode_step_count += 1

                # If done, stop the episode
                if done:
                    break

            # If for some reason there were no steps
            if episode_initial_epsilon is None:
                episode_initial_epsilon = current_epsilon
            episode_final_epsilon = current_epsilon
            
            # Loss mean of the episode
            avg_episode_loss = float(np.mean(episode_losses)) if episode_losses else math.nan

            # Add episode reward to the globah history
            episode_rewards.append(episode_reward)
            # Add end episode information
            info_str = "success" if info.get("successful", False) else "timeout" if info.get("timeout", False) else "failure"

            # Average rewards and loss of the last 10 episodes (reward/loss aware algoritm)
            avg_reward = float(np.mean(episode_rewards[-10:]))
            avg_loss = np.mean(losses[-10:]) if losses else math.nan

            # Episode information
            episode_elapsed_hours = float(info.get("elapsed_hours", getattr(env, "elapsed_hours", 0)))
            episode_total_dose = float(info.get("total_dose", getattr(env, "total_dose", 0.0)))
            episode_timeout = bool(info.get("timeout", False))
            episode_successful = bool(info.get("successful", False))
            episode_unsuccessful = bool(info.get("unsuccessful", False))

            # Adapt the optimizer learning rate only when reward-aware scheduling is enabled.
            previous_lr = float(agent.optimizer.param_groups[0]["lr"])
            if use_reward_aware:
                current_lr = agent.step_reward_scheduler(avg_reward)
                lr_reduced = current_lr < (previous_lr - 1e-12)
            else:
                current_lr = previous_lr
                lr_reduced = False

            # Append all episode metrics
            episode_metrics.append(
                {
                    "episode": episode,
                    "reward": episode_reward,
                    "epsilon_start": episode_initial_epsilon,
                    "epsilon_end": episode_final_epsilon,
                    "mean_loss": avg_episode_loss,
                    "learning_rate": current_lr,
                    "elapsed_hours": episode_elapsed_hours,
                    "timeout": episode_timeout,
                    "successful": episode_successful,
                    "unsuccessful": episode_unsuccessful,
                    "total_dose": episode_total_dose,
                    "steps": episode_step_count,
                    "updates": updates_this_episode,
                }
            )
            metrics_path = append_episode_metrics(metrics_log_path, (episode_metrics[-1],))

            # Change epsilon and epsilon decay moltiplication factor (reward aware algoritm)
            reward_adjustment = (
                epsilon_controller.update(avg_reward) if use_reward_aware and epsilon_controller is not None else None
            )

            # Print episode information
            print(
                f"Episode {episode:04d} | steps: {total_steps:06d} | ep_steps: {episode_step_count:04d} | updates: {updates_this_episode:03d} | "
                f"reward: {episode_reward:.3f} | avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | "
                f"lr: {current_lr:.6f} | eps: {current_epsilon:.3f} | elapsed_h: {episode_elapsed_hours:04.0f} | "
                f"dose: {episode_total_dose:.2f} | {info_str}"
            )

            # Print information of reduced learning rate
            if lr_reduced:
                print(
                    f"    Learning rate reduced from {previous_lr:.6f} to {current_lr:.6f} after reward plateau/decrease."
                )
                
            if reward_adjustment is not None and epsilon_log_path is not None and epsilon_controller is not None:
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
            
            # Periodically persist model, replay buffer, and metrics to disk.
            should_save_checkpoint = (episode % CHECKPOINT_INTERVAL == 0) or episode == config.episodes
            if should_save_checkpoint:
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
                if metrics_path is None:
                    metrics_path = metrics_log_path
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
                    f"{episode} -> model: {checkpoint_path}, buffer: {buffer_path}, metrics log: {metrics_log_path}"
                )

        # Guarantee at least one final checkpoint even if periodic saves were disabled.
        if metrics_path is None: # metrics_path is only set when saving a periodic checkpoint
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
            if episode_metrics:
                metrics_path = append_episode_metrics(metrics_log_path, episode_metrics)
            else:
                metrics_path = metrics_log_path if metrics_log_path.exists() else None
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
            print(f"Episode metrics appended to {metrics_log_path}")

        # Optionally evaluate the greedy policy after training completes.
        if config.eval_episodes > 0:
            mean_reward, success_rate = evaluate_policy(agent, env, config.eval_episodes, config.max_steps)
            print(
                f"Final evaluation -> mean reward: {mean_reward:.3f}, success rate: {success_rate:.2%}"
            )

        # Generate visual summaries to help inspect training dynamics.
        if metrics_path is not None:
            try:
                generate_training_plots(metrics_path)
            except Exception as plot_error:  # pragma: no cover - best-effort plotting
                print(f"Failed to generate training plots: {plot_error}")

        # Mark the run as completed so future invocations avoid resuming incorrectly.
        # Only if there are references to the last model and replay buffer checkpoints 
        #(last_checkpoint_path and last_buffer_path are not None)
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
    
    # Check keyboard input
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
