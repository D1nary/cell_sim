"""Gym wrappers for CellSimEnv.

These wrappers adapt action formatting and add light episode statistics
without pulling extra dependencies.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple, Sequence

import gymnasium as gym
import numpy as np


class ActionRounder(gym.Wrapper):
    """Round the second action component (wait hours) to an integer.

    Keeps the action within the base env's action_space bounds and casts
    hours to ``int`` for consistency.
    """

    def step(self, action):  # type: ignore[override]
        a = np.asarray(action, dtype=np.float32)
        # clip to the wrapped env action space bounds
        low, high = self.action_space.low, self.action_space.high
        a = np.clip(a, low, high)
        # round hours (index 1) to nearest integer
        if a.shape[0] >= 2:
            a[1] = float(int(round(float(a[1]))))
            # re-clip in case rounding exceeded bounds
            a[1] = float(np.clip(a[1], low[1], high[1]))
        return self.env.step(a)


class EpisodeStats(gym.Wrapper):
    """Collect simple per-episode stats and expose them via info.

    Adds cumulative reward and step count to the info dict at each step.
    Resets counters on env.reset().
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self._episode_return = 0.0
        self._episode_len = 0

    def reset(self, **kwargs):  # type: ignore[override]
        obs, info = self.env.reset(**kwargs)
        self._episode_return = 0.0
        self._episode_len = 0
        info = dict(info)
        info.update({
            "episode_return": 0.0,
            "episode_len": 0,
        })
        return obs, info

    def step(self, action):  # type: ignore[override]
        obs, rew, terminated, truncated, info = self.env.step(action)
        self._episode_return += float(rew)
        self._episode_len += 1
        info = dict(info)
        info.update({
            "episode_return": self._episode_return,
            "episode_len": self._episode_len,
        })
        return obs, rew, terminated, truncated, info


__all__ = [
    "ActionRounder",
    "EpisodeStats",
]


class DiscretizeAction(gym.Wrapper):
    """Map a Discrete action index to a continuous Box action vector.

    Provide a list/array of action vectors (shape: [n_actions, act_dim]).
    The wrapper exposes a Discrete(n_actions) action_space and internally
    forwards the corresponding continuous vector to the env.
    """

    def __init__(self, env: gym.Env, actions: np.ndarray):
        super().__init__(env)
        actions = np.asarray(actions, dtype=np.float32)
        assert actions.ndim == 2, "actions must be [n_actions, act_dim]"
        self._actions = actions
        self.action_space = gym.spaces.Discrete(actions.shape[0])

    def step(self, action):  # type: ignore[override]
        idx = int(action)
        if not (0 <= idx < self._actions.shape[0]):
            raise IndexError("Discrete action out of range")
        cont = self._actions[idx]
        return self.env.step(cont)


def build_discrete_action_grid(
    dose_values: Sequence[float],
    wait_values: Sequence[int],
) -> np.ndarray:
    """Cartesian product of dose and wait values -> action table.

    Returns an array of shape [n_actions, 2] with rows [dose, wait].
    """
    dose_values = np.asarray(dose_values, dtype=np.float32)
    wait_values = np.asarray(wait_values, dtype=np.int32)
    grid = np.stack(
        [
            np.repeat(dose_values, len(wait_values)),
            np.tile(wait_values, len(dose_values)),
        ],
        axis=1,
    ).astype(np.float32)
    return grid


__all__ += [
    "DiscretizeAction",
    "build_discrete_action_grid",
]
