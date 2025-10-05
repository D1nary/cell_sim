"""Project entry-point orchestrating training and evaluation for CellSim."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import pathlib

import numpy as np

from rein.agent.dqn_agent import DQNAgent
from rein.agent.train import (
    build_discrete_actions,
    evaluate_policy,
    linear_epsilon,
    resolve_device,
    run_training,
    seed_everything,
)
from rein.env.rl_env import CellSimEnv

# --- Create the directories ---
def create_directories(paths):
    for p in paths:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)


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
    device: str = "cuda"
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
    save_episodes: int = 50


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
        default=default_config.device,
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
        "--save-episodes",
        type=int,
        default=default_config.save_episodes,
        help="Checkpoint interval in episodes",
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
        device=args.device,
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
        save_episodes=args.save_episodes,
    )



def main() -> None:

    args = parse_args()
    config = build_config(args)
    device = resolve_device(config.device)

    # Setup directory
    script_dir = pathlib.Path(__file__).resolve().parent
    # project_root = script_dir.parent.parent
    res_path = script_dir / "results"
    data_path = res_path / "data"
    data_tab = data_path / "tabs"
    data_tab_growth = data_tab / "growth"
    data_tab_tr = data_tab / "therapy"
    res_agent = config.save_path
    paths = [str(res_path), str(data_path), str(data_tab),
             str(data_tab_growth), str(data_tab_tr),
             str(data_path / "cell_num"), str(res_agent)]

    # Directory cration
    create_directories(paths)

    # Training
    run_training(device)


    # try:j
    #     run_evaluation(agent, env, config.eval_episodes, config.max_steps)
    # finally:
    #     env.close()


if __name__ == "__main__":
    main()
