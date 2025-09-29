"""Reward functions for the RL environment.
This module implements the two families of reward functions:
"Killed" (K) and "Killed and Dose" (KD), for both regular and terminal steps.

Regular (non-terminal) formulas:
  K  = (#cancer_killed - x * #healthy_killed) / y
  KD = (#cancer_killed - x * #healthy_killed) / y - dose / z

Terminal step formulas:
  if the treatment was unsuccessful -> reward = -1
  otherwise
  K  = 0.5 - (H_init - H_final) / k
  KD = 0.5 - (H_init - H_final) / k - dose / z

The constants are:
  x = 5, y = 100_000, z = 200, k = 3_000.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RewardConsts:

    """Constants used in the reward formulas.
    """
    x: float = 5.0
    y: float = 100_000.0
    z: float = 200.0
    k: float = 3_000.0

DEFAULTS = RewardConsts()

def reward_k(
    cancer_killed: float,
    healthy_killed: float,
    *,
    x: float = DEFAULTS.x,
    y: float = DEFAULTS.y,
) -> float:
    """K reward for non-terminal steps.
    Parameters
    - cancer_killed: number of cancer cells killed in the step.
    - healthy_killed: number of healthy cells killed in the step.
    - x, y: constants of the formula.
    """
    return (float(cancer_killed) - x * float(healthy_killed)) / y

def reward_kd(
    cancer_killed: float,
    healthy_killed: float,
    dose: float,
    *,
    x: float = DEFAULTS.x,
    y: float = DEFAULTS.y,
    z: float = DEFAULTS.z,
) -> float:
    """KD reward for non-terminal steps (also penalizes dose).
    Parameters
    - cancer_killed: number of cancer cells killed in the step.
    - healthy_killed: number of healthy cells killed in the step.
    - dose: radiation dose delivered in the step.
    - x, y, z: constants of the formula.
    """
    return (float(cancer_killed) - x * float(healthy_killed)) / y - float(dose) / z

def terminal_reward_k(
    success: bool,
    healthy_initial: float,
    healthy_final: float,
    *,
    k: float = DEFAULTS.k,
) -> float:
    """K reward for terminal steps.
    If ``success`` is False, returns -1. Otherwise applies
    0.5 - (H_init - H_final) / k.
    """
    if not success:
        return -1.0
    return 0.5 - (float(healthy_initial) - float(healthy_final)) / k

def terminal_reward_kd(
    success: bool,
    healthy_initial: float,
    healthy_final: float,
    dose: float,
    *,
    k: float = DEFAULTS.k,
    z: float = DEFAULTS.z,
) -> float:
    """KD reward for terminal steps (also penalizes total dose).
    If ``success`` is False, returns -1. Otherwise applies
    0.5 - (H_init - H_final) / k - dose / z.
    """
    if not success:
        return -1.0
    return 0.5 - (float(healthy_initial) - float(healthy_final)) / k - float(dose) / z

__all__ = [
    "RewardConsts",
    "DEFAULTS",
    "reward_k",
    "reward_kd",
    "terminal_reward_k",
    "terminal_reward_kd",
]

