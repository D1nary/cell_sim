"""Training entry-point for the DQN agent on the `CellSimEnv` environment."""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch

from .dqn_agent import DQNAgent, DQNConfig
from ..env import CellSimEnv


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the training script."""
    parser = argparse.ArgumentParser(description="Train a DQN agent for CellSimEnv")
    parser.add_argument("--episodes", type=int, default=500, help="Number of training episodes")
    parser.add_argument("--max-steps", type=int, default=1_200, help="Maximum number of steps per episode")
    parser.add_argument("--seed", type=int, default=0, help="Initialization seed")
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=("cpu", "cuda", "auto"),
        help="Device to use (CPU by default). Use 'auto' to prefer CUDA when available",
    )
    parser.add_argument("--dose-bins", type=int, default=5, help="Number of discretization bins for the dose")
    parser.add_argument("--wait-bins", type=int, default=6, help="Number of discretization bins for the wait time")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor gamma")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate for the optimizer")
    parser.add_argument("--batch-size", type=int, default=64, help="Mini-batch size")
    parser.add_argument("--buffer-size", type=int, default=100_000, help="Experience replay capacity")
    parser.add_argument(
        "--warmup-steps",
        type=int,
        default=5_000,
        help="Minimum transitions in the buffer before updates",
    )
    parser.add_argument("--target-update", type=int, default=1_000, help="Target network update interval")
    parser.add_argument("--epsilon-start", type=float, default=1.0, help="Initial epsilon value")
    parser.add_argument("--epsilon-end", type=float, default=0.05, help="Minimum epsilon value")
    parser.add_argument(
        "--epsilon-decay-steps",
        type=int,
        default=100_000,
        help="Number of steps for the linear epsilon decay",
    )
    parser.add_argument(
        "--eval-episodes",
        type=int,
        default=5,
        help="Number of greedy evaluation episodes after training",
    )
    parser.add_argument(
        "--save-path",
        type=Path,
        default=Path("results/dqn_agent.pt"),
        help="Path where to save the agent weights",
    )
    parser.add_argument(
        "--growth-hours",
        type=int,
        default=150,
        help="Number of growth hours applied to the resetted environment",
    )
    return parser.parse_args()


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


def main() -> None:
    """Run the full DQN training loop and optional evaluation."""
    # Gather CLI configuration and lock reproducible behaviour.
    args = parse_args()
    device = resolve_device(args.device)
    seed_everything(args.seed)

    # Build the environment and discretised action catalogue used by the DQN.
    env = CellSimEnv()
    discrete_actions = build_discrete_actions(env.action_space, args.dose_bins, args.wait_bins)
    state_dim = int(np.prod(env.observation_space.shape)) # type: ignore

    # Instantiate the agent with hyperparameters from the CLI.
    config = DQNConfig(
        gamma=args.gamma,
        learning_rate=args.lr,
        batch_size=args.batch_size,
        buffer_size=args.buffer_size,
        min_buffer_size=args.warmup_steps,
        target_update_interval=args.target_update,
    )
    agent = DQNAgent(state_dim, discrete_actions, device, config)

    total_steps = 0
    episode_rewards: List[float] = []
    losses: List[float] = []

    # Main training loop over episodes.
    for episode in range(1, args.episodes + 1):

        # Reset the grid to the initial state
        state, _ = env.reset(seed=args.seed + episode)
        # Perform a new growth to the environment
        env.growth(args.growth_hours)
        
        episode_reward = 0.0
        info = {}

        current_epsilon = args.epsilon_start  # Default value for Pylance error

        for _ in range(args.max_steps):

            # Compute the current epsilon for the epsilon-greedy policy and select an action.
            current_epsilon = linear_epsilon(total_steps, args.epsilon_start, args.epsilon_end, args.epsilon_decay_steps)
            action_idx, action = agent.select_action(state, current_epsilon)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # Store the transition and, if ready, run a learning update.
            agent.store_transition(state, action_idx, reward, next_state, done)

            # Update of DQN
            loss = agent.update()

            if loss is not None:
                losses.append(loss)

            state = next_state
            episode_reward += reward
            total_steps += 1

            if done:
                break

        episode_rewards.append(episode_reward)
        info_str = "success" if info.get("successful", False) else "timeout" if info.get("timeout", False) else "failure"
        avg_reward = np.mean(episode_rewards[-10:])
        avg_loss = np.mean(losses[-10:]) if losses else math.nan
        
        print(
            f"Episode {episode:04d} | steps: {total_steps:06d} | reward: {episode_reward:.3f} | "
            f"avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | eps: {current_epsilon:.3f} | {info_str}"
        )


    # Saving data
    # Root is considered the path of the main script’s directory
    args.save_path.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(args.save_path))
    print(f"Model saved to {args.save_path}")

    if args.eval_episodes > 0:
        mean_reward, success_rate = evaluate_policy(agent, env, args.eval_episodes, args.max_steps)
        print(
            f"Final evaluation -> mean reward: {mean_reward:.3f}, success rate: {success_rate:.2%}"
        )

    env.close()


if __name__ == "__main__":
    main()
