"""Minimal training script for CellSimEnv.

This draft uses a simple random policy baseline and a lightweight loop
that is easy to replace with a real agent (e.g., SAC/TD3/PPO).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import gym
import numpy as np

from .config import TrainConfig, default_config
from .policies import DQNAgent
from .utils import seed_everything, make_run_dir, save_json
from .wrappers import ActionRounder, EpisodeStats, DiscretizeAction, build_discrete_action_grid
from .replay_buffer import ReplayBuffer
from .callbacks import StopOnSuccessRate


def make_env(cfg: TrainConfig) -> gym.Env:
    # Local import to avoid import-time issues if cell_sim isn't on sys.path
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

    # Discretize continuous action space for DQN
    dose_vals = np.linspace(0.0, cfg.env.max_dose, cfg.env.action_bins_dose, dtype=np.float32)
    wait_vals = np.linspace(0, cfg.env.max_wait, cfg.env.action_bins_wait, dtype=np.int32)
    wait_vals = np.unique(np.clip(np.round(wait_vals).astype(int), 0, cfg.env.max_wait))
    action_table = build_discrete_action_grid(dose_vals, wait_vals)
    env = DiscretizeAction(env, actions=action_table)
    return env


def train(cfg: TrainConfig) -> Path:
    # Reproducibility
    seed_everything(cfg.seed)

    # Outputs
    run_dir = make_run_dir(cfg.project_dir, cfg.run_name)
    save_json(run_dir / "config.json", cfg)

    # Env and DQN agent
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
        eps_start=cfg.eps_start,
        eps_end=cfg.eps_end,
        eps_decay_steps=cfg.eps_decay_steps,
    )
    buffer = ReplayBuffer(capacity=cfg.buffer_size, obs_shape=obs_shape)

    # Optional early stopping (disabled by default; enable by editing below)
    callbacks: Iterable = (StopOnSuccessRate(window=10, threshold=0.95),)

    # Training loop (episode-based)
    global_step = 0
    summary = []
    for ep in range(1, cfg.total_episodes + 1):
        obs, info = env.reset(seed=cfg.seed + ep)
        ep_return = 0.0
        ep_len = 0
        terminated = truncated = False

        for t in range(cfg.max_steps_per_episode):
            action = int(agent.act(np.asarray(obs, dtype=np.float32)))
            next_obs, reward, terminated, truncated, info = env.step(action)
            ep_return += float(reward)
            ep_len += 1
            global_step += 1
            done = bool(terminated or truncated)
            buffer.add(np.asarray(obs, dtype=np.float32), action, float(reward), np.asarray(next_obs, dtype=np.float32), done)

            # Learning step
            if len(buffer) >= max(cfg.learning_starts, cfg.batch_size) and (global_step % cfg.train_freq == 0):
                batch = buffer.sample(cfg.batch_size)
                loss = agent.update(batch, agent.target_net, cfg.gamma)
                # Periodic target net sync
                if global_step % cfg.target_update_freq == 0:
                    agent.sync_target()

            obs = next_obs
            if terminated or truncated:
                break

        # Episode summary
        record = {
            "episode": ep,
            "return": ep_return,
            "length": ep_len,
            "successful": bool(info.get("successful", False)),
            "unsuccessful": bool(info.get("unsuccessful", False)),
            "timeout": bool(info.get("timeout", False)),
            "elapsed_hours": int(info.get("elapsed_hours", 0)),
        }
        summary.append(record)

        # Callbacks
        for cb in callbacks:
            try:
                cb.on_episode_end(info=info)
            except Exception:
                pass

        # Periodic save of summary and checkpoint
        if ep % max(1, cfg.save_every_episodes) == 0:
            save_json(run_dir / "summary.json", summary)
            try:
                agent.save(str(run_dir / "dqn.pt"))
            except Exception:
                pass

        # Optional early stop
        if any(getattr(cb, "should_stop", lambda: False)() for cb in callbacks):
            break

    # Final save
    save_json(run_dir / "summary.json", summary)
    try:
        agent.save(str(run_dir / "dqn.pt"))
    except Exception:
        pass
    env.close()
    return run_dir


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train a policy in CellSimEnv")
    p.add_argument("--run-name", type=str, default="debug", help="Run name suffix")
    p.add_argument("--episodes", type=int, default=None, help="Total episodes")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = default_config()
    if args.run_name is not None:
        cfg.run_name = args.run_name
    if args.episodes is not None:
        cfg.total_episodes = int(args.episodes)
    if args.seed is not None:
        cfg.seed = int(args.seed)

    out = train(cfg)
    print(f"Training finished. Results saved to: {out}")


if __name__ == "__main__":
    main()
