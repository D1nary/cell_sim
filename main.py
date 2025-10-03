"""Project entry-point orchestrating training and evaluation for CellSim."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np

from rein.agent.dqn_agent import DQNAgent
from rein.agent.train import (
    build_discrete_actions,
    evaluate_policy,
    linear_epsilon,
    resolve_device,
    seed_everything,
)
from rein.env.rl_env import CellSimEnv


@dataclass
class AIConfig:
    """Consolidated DQN training hyper-parameters."""

    gamma: float = 0.99
    learning_rate: float = 1e-3
    batch_size: int = 64
    buffer_size: int = 50_000
    min_buffer_size: int = 1_000
    target_update_interval: int = 1_000
    hidden_sizes: Tuple[int, ...] = (256, 256)
    gradient_clip: float | None = 10.0
    seed: int = 1
    dose_bins: int = 5
    wait_bins: int = 6
    episodes: int = 500
    growth_hours: int = 150
    max_steps: int = 1_200
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_steps: int = 100_000
    save_path: Path = Path("results/dqn_agent.pt")
    eval_episodes: int = 5


def prepare_simulation_dirs(_output_dir: Path) -> None:
    """Placeholder for filesystem preparation logic."""
    # Implementation will handle directory creation and cleanup.
    pass


def parse_optional_float(value: str) -> float | None:
    """Parse a float that can be disabled with the literal 'none'."""
    if value.lower() in {"none", "null"}:
        return None
    return float(value)


def parse_int_sequence(value: str) -> Tuple[int, ...]:
    """Parse a comma or space separated sequence of integers."""
    cleaned = value.replace(",", " ")
    parts = [int(part) for part in cleaned.split() if part]
    if not parts:
        raise argparse.ArgumentTypeError("Provide at least one integer")
    return tuple(parts)


def parse_args() -> argparse.Namespace:
    """Configure and parse command line arguments for the entry-point."""
    default_config = AIConfig()

    parser = argparse.ArgumentParser(description="Train and evaluate a DQN agent on CellSim")

    parser.add_argument("--episodes", type=int, default=default_config.episodes, help="Number of training episodes")
    parser.add_argument("--max-steps", type=int, default=default_config.max_steps, help="Maximum number of steps per episode")
    parser.add_argument("--seed", type=int, default=default_config.seed, help="Initialization seed")
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=("cpu", "cuda", "auto"),
        help="Device to use (CPU by default). Use 'auto' to prefer CUDA when available",
    )
    parser.add_argument(
        "--dose-bins",
        type=int,
        default=default_config.dose_bins,
        help="Number of discretization bins for the dose",
    )
    parser.add_argument(
        "--wait-bins",
        type=int,
        default=default_config.wait_bins,
        help="Number of discretization bins for the wait time",
    )
    parser.add_argument(
        "--eval-episodes",
        type=int,
        default=default_config.eval_episodes,
        help="Number of greedy evaluation episodes",
    )
    parser.add_argument(
        "--save-path",
        type=Path,
        default=default_config.save_path,
        help="Destination path for the trained agent weights",
    )
    parser.add_argument(
        "--growth-hours",
        type=int,
        default=default_config.growth_hours,
        help="Number of growth hours applied to the environment before each episode",
    )

    # Agent overrides
    parser.add_argument("--agent-gamma", type=float, default=default_config.gamma, help="Discount factor gamma")
    parser.add_argument(
        "--agent-learning-rate",
        type=float,
        default=default_config.learning_rate,
        help="Optimizer learning rate",
    )
    parser.add_argument(
        "--agent-target-update",
        type=int,
        default=default_config.target_update_interval,
        help="Target network update interval (steps)",
    )
    parser.add_argument(
        "--agent-epsilon-start",
        type=float,
        default=default_config.epsilon_start,
        help="Initial epsilon value",
    )
    parser.add_argument(
        "--agent-epsilon-end",
        type=float,
        default=default_config.epsilon_end,
        help="Final epsilon value",
    )
    parser.add_argument(
        "--agent-epsilon-decay-steps",
        type=int,
        default=default_config.epsilon_decay_steps,
        help="Number of steps over which epsilon decays",
    )
    parser.add_argument(
        "--agent-gradient-clip",
        type=parse_optional_float,
        default=default_config.gradient_clip,
        help="Gradient clipping value; use 'none' to disable",
    )

    # Replay buffer overrides
    parser.add_argument(
        "--replay-capacity",
        type=int,
        default=default_config.buffer_size,
        help="Maximum number of transitions stored",
    )
    parser.add_argument(
        "--replay-min-size",
        type=int,
        default=default_config.min_buffer_size,
        help="Minimum transitions before learning starts",
    )
    parser.add_argument(
        "--replay-batch-size",
        type=int,
        default=default_config.batch_size,
        help="Mini-batch size for updates",
    )

    # Model overrides
    parser.add_argument(
        "--model-hidden-sizes",
        type=parse_int_sequence,
        default=default_config.hidden_sizes,
        help="Comma or space separated hidden layer sizes (default: 256,256)",
    )

    return parser.parse_args()


def build_config(args: argparse.Namespace) -> AIConfig:
    """Materialise the training configuration from CLI arguments."""
    hidden_sizes = tuple(args.model_hidden_sizes)
    return AIConfig(
        gamma=args.agent_gamma,
        learning_rate=args.agent_learning_rate,
        batch_size=args.replay_batch_size,
        buffer_size=args.replay_capacity,
        min_buffer_size=args.replay_min_size,
        target_update_interval=args.agent_target_update,
        hidden_sizes=hidden_sizes,
        gradient_clip=args.agent_gradient_clip,
        seed=args.seed,
        dose_bins=args.dose_bins,
        wait_bins=args.wait_bins,
        episodes=args.episodes,
        growth_hours=args.growth_hours,
        max_steps=args.max_steps,
        epsilon_start=args.agent_epsilon_start,
        epsilon_end=args.agent_epsilon_end,
        epsilon_decay_steps=args.agent_epsilon_decay_steps,
        save_path=args.save_path,
        eval_episodes=args.eval_episodes,
    )


def run_training(config: AIConfig, args: argparse.Namespace) -> tuple[DQNAgent, CellSimEnv]:
    """Execute the DQN training loop and persist the resulting policy."""
    device = resolve_device(args.device)
    seed_everything(config.seed)

    env = CellSimEnv()
    discrete_actions = build_discrete_actions(env.action_space, config.dose_bins, config.wait_bins)
    state_dim = int(np.prod(env.observation_space.shape))

    agent = DQNAgent(state_dim, discrete_actions, device, config)

    total_steps = 0
    episode_rewards: list[float] = []
    losses: list[float] = []

    for episode in range(1, config.episodes + 1):
        state, _ = env.reset(seed=config.seed + episode)
        env.growth(config.growth_hours)

        episode_reward = 0.0
        info: dict[str, object] = {}
        current_epsilon = config.epsilon_start

        for _ in range(config.max_steps):
            current_epsilon = linear_epsilon(
                total_steps,
                config.epsilon_start,
                config.epsilon_end,
                config.epsilon_decay_steps,
            )
            action_idx, action = agent.select_action(state, current_epsilon)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            agent.store_transition(state, action_idx, reward, next_state, done)
            loss = agent.update()
            if loss is not None:
                losses.append(loss)

            state = next_state
            episode_reward += reward
            total_steps += 1

            if done:
                break

        episode_rewards.append(episode_reward)
        avg_reward = float(np.mean(episode_rewards[-10:]))
        avg_loss = float(np.mean(losses[-10:])) if losses else math.nan
        outcome = "success" if info.get("successful") else "timeout" if info.get("timeout") else "failure"
        print(
            f"Episode {episode:04d} | steps: {total_steps:06d} | reward: {episode_reward:.3f} | "
            f"avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | eps: {current_epsilon:.3f} | {outcome}"
        )

    config.save_path.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(config.save_path))
    print(f"Model saved to {config.save_path}")

    return agent, env


def run_evaluation(agent: DQNAgent, env: CellSimEnv, episodes: int, max_steps: int) -> tuple[float, float] | None:
    """Evaluate the trained policy when episodes are requested."""
    if episodes <= 0:
        return None
    mean_reward, success_rate = evaluate_policy(agent, env, episodes, max_steps)
    print(f"Evaluation -> mean reward: {mean_reward:.3f}, success rate: {success_rate:.2%}")
    return mean_reward, success_rate


def main() -> None:
    args = parse_args()
    config = build_config(args)
    prepare_simulation_dirs(config.save_path.parent)
    agent, env = run_training(config, args)
    try:
        run_evaluation(agent, env, config.eval_episodes, config.max_steps)
    finally:
        env.close()


if __name__ == "__main__":
    main()
