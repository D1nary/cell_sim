"""Reinforcement learning environment for the cell simulator.

This module defines :class:`CellSimEnv`, a placeholder Gym-compatible
environment for controllin radiation treatment.
"""

from __future__ import annotations

import gym
from gym import spaces
import numpy as np
import cell_sim


class CellSimEnv(gym.Env):
    """Environment wrapper around :mod:`cell_sim`.

    The environment provides a Gym-compatible interface where actions are
    tuples of radiation ``dose`` and ``wait_hours`` to advance the
    simulation.
    """

    def __init__(
        self,
        xsize: int = 21,
        ysize: int = 21,
        zsize: int = 21,
        sources_num: int = 20,
        cradius: float = 2.0,
        hradius: float = 4.0,
        hcells: int = 1,
        ccells: int = 1,
        max_dose: float = 2.0,
        max_wait: int = 24,
    ) -> None:
        """Create the simulation controller and define spaces.

        Parameters
        ----------
        xsize, ysize, zsize : int
            Grid dimensions for the simulator.
        sources_num : int
            Number of radiation sources in the grid.
        cradius, hradius : float
            Radii used for the cancer and healthy regions.
        hcells, ccells : int
            Initial number of healthy and cancer cells per voxel.
        max_dose : float
            Maximum radiation dose deliverable in a single step.
        max_wait : int
            Maximum number of hours to advance the simulation after dosing.
        """

        super().__init__()

        # Simulator controller
        self.ctrl = cell_sim.Controller(
            xsize,
            ysize,
            zsize,
            sources_num,
            cradius,
            hradius,
            hcells,
            ccells,
        )

        # Action is (dose, wait_hours)
        self.max_dose = float(max_dose)
        self.max_wait = int(max_wait)
        # Tracks cumulative simulated hours to detect timeout
        self.elapsed_hours = 0
        self.action_space = spaces.Box(
            low=np.array([0.0, 0.0], dtype=np.float32),
            high=np.array([self.max_dose, float(self.max_wait)], dtype=np.float32),
            dtype=np.float32,
        )

        # Observation: counts of healthy and cancer cells (healthy, cancer)
        self.observation_space = spaces.Box(
            low=0.0,
            high=np.inf,
            shape=(2,),
            dtype=np.float32,
        )

    def reset(self):
        """Reset the simulation and return the initial observation."""
        # TODO: implement reset logic
        pass

    def step(self, action):
        """Apply an action and advance the simulation."""
        # Action is (dose, wait_hours)
        a = np.asarray(action, dtype=np.float32)
        dose = float(np.clip(a[0], 0.0, self.max_dose))
        hours = int(np.clip(a[1], 0.0, float(self.max_wait)))

        # Irradiate with the given dose
        if dose > 0.0:
            self.ctrl.irradiate(dose)

        # Advance simulation for the specified number of hours
        for _ in range(hours):
            self.ctrl.go()
        # Update cumulative time
        self.hour_count += hours

        # Observation: total healthy and cancer cell counts
        counts = self.ctrl.get_cell_counts()
        observation = np.asarray(counts, dtype=np.float32)

        # Terminal conditions based on observation and elapsed time
        # Evaluate raw flags first
        _successful = bool(observation[1] == 0)
        _unsuccessful = bool(observation[0] <= 10)
        _timeout = bool(self.elapsed_hours >= 1200)

        # Enforce mutually-exclusive terminal reason, prioritizing success, then failure
        if _successful:
            successful, unsuccessful, timeout = True, False, False
        elif _unsuccessful:
            successful, unsuccessful, timeout = False, True, False
        elif _timeout:
            successful, unsuccessful, timeout = False, False, True
        else:
            successful, unsuccessful, timeout = False, False, False

        # Terminated if success or failure; truncated if only timeout
        terminated = successful or unsuccessful
        truncated = timeout

        # Placeholder reward; actual shaping can be plugged from rein/reward.py
        reward = 0.0

        # Provide all flags and counters in info for downstream logic/analysis
        info = {
            "successful": successful,
            "unsuccessful": unsuccessful,
            "timeout": timeout,
            "elapsed_hours": self.elapsed_hours,
        }
        return observation, reward, terminated, truncated, info

    def close(self):
        """Release resources and perform any necessary cleanup."""
        # TODO: implement close logic
        pass
