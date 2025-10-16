"""Project entry-point orchestrating training and evaluation for CellSim."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple
import pathlib

import numpy as np

from rein.agent.core import DQNAgent
from rein.agent.train import (
    build_discrete_actions,
    evaluate_policy,
    linear_epsilon,
    resolve_device,
    run_training,
    seed_everything,
)
from rein.agent.metrics import (
    plot_epsilon,
    plot_episode_rewards,
    plot_learning_rate,
    plot_q_values,
    plot_td_loss,
)
from rein.env.rl_env import CellSimEnv
from rein.configs import AIConfig

# --- Create the directories ---
def create_directories(paths):
    for p in paths:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)


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
        "--min-dose",
        type=float,
        default=default_config.min_dose,
        help="Minimum radiation dose allowed per action",
    )
    parser.add_argument(
        "--max-dose",
        type=float,
        default=default_config.max_dose,
        help="Maximum radiation dose allowed per action",
    )
    parser.add_argument(
        "--wait-bins",
        type=int,
        default=default_config.wait_bins,
        help="Number of discretization bins for the wait time",
    )
    parser.add_argument(
        "--min-wait",
        type=int,
        default=default_config.min_wait,
        help="Minimum wait time (in hours) allowed per action",
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=default_config.max_wait,
        help="Maximum wait time (in hours) allowed per action",
    )
    parser.add_argument(
        "--eval-episodes",
        type=int,
        default=default_config.eval_episodes,
        help="Number of greedy evaluation episodes",
    )
    parser.add_argument(
        "--save-agent-path",
        type=Path,
        default=default_config.save_agent_path,
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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume training from the most recent checkpoint",
    )
    parser.add_argument(
        "--resume-from",
        type=Path,
        default=default_config.resume_from,
        help="Override the checkpoint directory used when resuming",
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

    parser.add_argument(
        "--plot",
        choices=("reward", "loss", "epsilon", "q-values", "learning-rate", "all"),
        action="append",
        help="Render selected training plots from metrics CSV and exit (repeat for multiple). Use 'all' for every plot.",
    )
    parser.add_argument(
        "--plot-metrics-path",
        type=Path,
        help="Path to the metrics CSV used for plotting (defaults to <save_agent_path>/agent/agent_final_metrics.csv).",
    )
    parser.add_argument(
        "--plot-output-dir",
        type=Path,
        help="Destination directory for generated plots (defaults to the metrics directory).",
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
        min_dose=args.min_dose,
        max_dose=args.max_dose,
        min_wait=args.min_wait,
        max_wait=args.max_wait,
        episodes=args.episodes,
        growth_hours=args.growth_hours,
        max_steps=args.max_steps,
        epsilon_start=args.agent_epsilon_start,
        epsilon_end=args.agent_epsilon_end,
        epsilon_decay_steps=args.agent_epsilon_decay_steps,
        save_agent_path=args.save_agent_path,
        eval_episodes=args.eval_episodes,
        save_episodes=args.save_episodes,
        resume=args.resume,
        resume_from=args.resume_from,
    )



def render_plots_from_cli(args: argparse.Namespace) -> None:
    """Generate requested plots based on CLI options."""

    metrics_path = args.plot_metrics_path
    if metrics_path is None:
        metrics_path = args.save_agent_path / "agent" / "agent_final_metrics.csv"
    metrics_path = Path(metrics_path)
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

    output_dir = Path(args.plot_output_dir) if args.plot_output_dir is not None else metrics_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    available_plots = {
        "reward": (plot_episode_rewards, "reward.png"),
        "loss": (plot_td_loss, "loss.png"),
        "epsilon": (plot_epsilon, "epsilon.png"),
        "q-values": (plot_q_values, "q_values.png"),
        "learning-rate": (plot_learning_rate, "learning_rate.png"),
    }

    requested = args.plot or []
    if not requested:
        return

    # Expand "all" into the full set while preserving order and uniqueness.
    selected: list[str] = []
    for entry in requested:
        if entry == "all":
            for key in available_plots:
                if key not in selected:
                    selected.append(key)
        elif entry not in selected:
            selected.append(entry)

    print(f"Generating plots from metrics: {metrics_path}")
    saved_any = False
    for key in selected:
        plotter, filename = available_plots[key]
        destination = output_dir / filename
        try:
            plotter(metrics_path, save_to=destination)
            print(f" - {key}: {destination}")
            saved_any = True
        except Exception as error:
            print(f" ! Failed to render {key}: {error}")

    if saved_any:
        print(f"Plots saved to: {output_dir}")
    else:
        print("No plots were generated.")


def main() -> None:

    args = parse_args()

    if args.plot:
        render_plots_from_cli(args)
        return

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
    res_agent_parent = config.save_agent_path
    res_agent = res_agent_parent / "agent"
    res_buffer = res_agent_parent / "buffer"
    paths = [
        res_path,
        data_path,
        data_tab,
        data_tab_growth,
        data_tab_tr,
        data_path / "cell_num",
        res_agent_parent,
        res_agent,
        res_buffer,
    ]

    # Directory cration
    create_directories(paths)

    # Training
    run_training(config, device)


    # try:j
    #     run_evaluation(agent, env, config.eval_episodes, config.max_steps)
    # finally:
    #     env.close()


if __name__ == "__main__":
    main()
