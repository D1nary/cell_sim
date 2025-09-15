"""Evaluate a policy on CellSimEnv episodes.

This draft runs a random baseline unless a custom policy is wired in.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import gymnasium as gym
import numpy as np

from .config import TrainConfig, default_config
from .policies import DQNAgent
from .utils import seed_everything
from .wrappers import ActionRounder, EpisodeStats, DiscretizeAction, build_discrete_action_grid


def make_env(cfg: TrainConfig) -> gym.Env:
    from .rl_env import CellSimEnv
    env = CellSimEnv(
        xsize=cfg.env.xsize,
        ysize=cfg.env.ysize,
        zsize=cfg.env.zsize,
        sources_num=cfg.env.sources_num,
        cradius=cfg.env.cradius,
        hradius=cfg.env.hradius,
        hcells=cfg.env.hcells,
        ccells=cfg.env.ccells,
        max_dose=cfg.env.max_dose,
        max_wait=cfg.env.max_wait,
    )
    env = ActionRounder(env)
    env = EpisodeStats(env)
    dose_vals = np.linspace(0.0, cfg.env.max_dose, cfg.env.action_bins_dose, dtype=np.float32)
    wait_vals = np.linspace(0, cfg.env.max_wait, cfg.env.action_bins_wait, dtype=np.int32)
    wait_vals = np.unique(np.clip(np.round(wait_vals).astype(int), 0, cfg.env.max_wait))
    action_table = build_discrete_action_grid(dose_vals, wait_vals)
    env = DiscretizeAction(env, actions=action_table)
    return env


def evaluate(cfg: TrainConfig, episodes: int = 5) -> List[dict]:
    seed_everything(cfg.seed)
    env = make_env(cfg)
    assert isinstance(env.action_space, gym.spaces.Discrete)
    obs_shape = env.observation_space.shape
    obs_dim = int(np.prod(obs_shape))
    n_actions = int(env.action_space.n)
    agent = DQNAgent(
        obs_dim=obs_dim,
        n_actions=n_actions,
        lr=cfg.lr,
        gamma=cfg.gamma,
        eps_start=0.0,  # greedy at eval
        eps_end=0.0,
        eps_decay_steps=1,
    )
    # Try to load default checkpoint path
    try:
        from pathlib import Path
        ckpt = Path("results/rl").rglob("dqn.pt")
        ckpt = next(ckpt)  # first match
        agent.load(str(ckpt))
        print(f"Loaded checkpoint: {ckpt}")
    except Exception:
        print("No checkpoint found; evaluating untrained agent")

    results: List[dict] = []
    for ep in range(1, episodes + 1):
        obs, info = env.reset(seed=cfg.seed + ep)
        terminated = truncated = False
        ep_return = 0.0
        ep_len = 0

        while not (terminated or truncated):
            action = int(agent.act(np.asarray(obs, dtype=np.float32), deterministic=True))
            obs, reward, terminated, truncated, info = env.step(action)
            ep_return += float(reward)
            ep_len += 1

        results.append({
            "episode": ep,
            "return": ep_return,
            "length": ep_len,
            "successful": bool(info.get("successful", False)),
            "unsuccessful": bool(info.get("unsuccessful", False)),
            "timeout": bool(info.get("timeout", False)),
            "elapsed_hours": int(info.get("elapsed_hours", 0)),
        })

    env.close()
    return results


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate a policy on CellSimEnv")
    p.add_argument("--episodes", type=int, default=5, help="Episodes to run")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    args = p.parse_args()

    cfg = default_config()
    if args.seed is not None:
        cfg.seed = int(args.seed)

    results = evaluate(cfg, episodes=int(args.episodes))
    mean_return = sum(r["return"] for r in results) / max(1, len(results))
    print(f"Ran {len(results)} episodes. Mean return: {mean_return:.3f}")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
