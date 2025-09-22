from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .agent import PPOAgent
from .config import PPOConfig
from .rl_env import CellSimEnv
from .utils import ensure_dir, format_metrics, select_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PPO agent for radiotherapy dosing")
    parser.add_argument("--total-steps", type=int, default=PPOConfig.total_timesteps, help="Total environment steps")
    parser.add_argument("--rollout-steps", type=int, default=PPOConfig.rollout_steps, help="Steps collected before each policy update")
    parser.add_argument("--minibatch-size", type=int, default=PPOConfig.minibatch_size, help="PPO minibatch size")
    parser.add_argument("--learning-rate", type=float, default=PPOConfig.learning_rate, help="Optimizer learning rate")
    parser.add_argument("--device", type=str, default=PPOConfig.device, help="Device to run on: auto|cpu|cuda|mps")
    parser.add_argument("--seed", type=int, default=PPOConfig.seed, help="Random seed")
    parser.add_argument("--eval-interval", type=int, default=PPOConfig.eval_interval, help="Steps between evaluation sweeps")
    parser.add_argument("--checkpoint", type=Path, default=None, help="Where to store the best model weights")
    parser.add_argument("--max-dose", type=float, default=None, help="Override environment max dose")
    parser.add_argument("--max-wait", type=float, default=None, help="Override environment max wait hours")
    parser.add_argument("--log-config", type=Path, default=None, help="Dump resolved config to JSON file")
    return parser.parse_args()


def build_env(args: argparse.Namespace) -> tuple[CellSimEnv, Dict[str, Any]]:
    env_kwargs: Dict[str, Any] = {}
    if args.max_dose is not None:
        env_kwargs["max_dose"] = float(args.max_dose)
    if args.max_wait is not None:
        env_kwargs["max_wait"] = int(args.max_wait)
    env = CellSimEnv(**env_kwargs)
    return env, env_kwargs


def main() -> None:
    args = parse_args()

    config = PPOConfig(
        total_timesteps=args.total_steps,
        rollout_steps=args.rollout_steps,
        minibatch_size=args.minibatch_size,
        learning_rate=args.learning_rate,
        device=args.device,
        seed=args.seed,
        eval_interval=args.eval_interval,
    )
    if args.checkpoint is not None:
        config.checkpoint_path = args.checkpoint
    config.ensure_minibatch()

    device = select_device(config.device)
    print(f"[train] Using device {device}")

    set_seed(config.seed)
    env, env_kwargs = build_env(args)

    def env_factory() -> CellSimEnv:
        return CellSimEnv(**env_kwargs)

    agent = PPOAgent(env=env, config=config, device=device, env_factory=env_factory)

    try:
        final_metrics = agent.train()
    except KeyboardInterrupt:
        print("[train] Interrupted by user; performing final evaluation")
        final_metrics = agent.evaluate()
    finally:
        env.close()

    if args.log_config is not None:
        ensure_dir(args.log_config.parent)
        with args.log_config.open("w", encoding="utf-8") as fp:
            json.dump(asdict(config), fp, indent=2)

    print(f"[train] Completed | {format_metrics(final_metrics)}")


if __name__ == "__main__":
    main()
