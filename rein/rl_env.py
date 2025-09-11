"""Reinforcement learning environment for the cell simulator.

This module defines :class:`CellSimEnv`, a placeholder Gym-compatible
environment for controllin radiation treatment.
"""

from __future__ import annotations

import gym
from gym import spaces
import numpy as np

import cell_sim

from .reward import reward_kd, terminal_reward_kd


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
        """Reset cached state and return the current observation.

        Note: the underlying simulator does not expose a full reset API,
        so this method reinitializes only the environment bookkeeping.
        """
        counts = self.ctrl.get_cell_counts()
        self.initial_healthy = float(counts[0])
        self.prev_counts = tuple(map(float, counts))
        self.elapsed_hours = 0
        self.total_dose = 0.0
        return np.asarray(counts, dtype=np.float32)

    def step(self, action):
        """Apply an action and advance the simulation."""
        # Action is (dose, wait_hours)
        a = np.asarray(action, dtype=np.float32)
        dose = float(np.clip(a[0], 0.0, self.max_dose))
        hours = int(np.clip(a[1], 0.0, float(self.max_wait)))

        # Compute healthy and cancer cells count before the radiation
        counts = self.ctrl.get_cell_counts()
        counts = np.asarray(counts, dtype=np.float32)
        prev_h, prev_c = float(counts[0]), float(counts[1])

        # Irradiate with the given dose
        if dose > 0.0:
            self.ctrl.irradiate(dose)
            self.total_dose = float(getattr(self, "total_dose", 0.0) + dose)

        # Advance simulation for the specified number of hours
        for _ in range(hours):
            self.ctrl.go()
        # Update cumulative time
        self.elapsed_hours = int(getattr(self, "elapsed_hours", 0) + hours)

        # Observation: total healthy and cancer cell counts
        counts = self.ctrl.get_cell_counts()
        observation = np.asarray(counts, dtype=np.float32)
        healthy, cancer = float(observation[0]), float(observation[1])

        # Terminal conditions based on observation and elapsed time
        # Evaluate raw flags first
        _successful = bool(cancer == 0)
        _unsuccessful = bool(healthy <= 10)
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

        # Compute reward using functions from rein/reward.py
        # Step deltas (killed counts in this step)
        # prev_h, prev_c = getattr(self, "prev_counts", (healthy, cancer))
        healthy_killed = max(0.0, float(prev_h) - healthy)
        cancer_killed = max(0.0, float(prev_c) - cancer)

        if not terminated and not truncated:
            # Non-terminal step: KD reward using this step dose
            reward = reward_kd(cancer_killed, healthy_killed, dose)
        elif terminated and successful:
            # Terminal successful: KD terminal reward (penalize total dose)
            init_h = float(getattr(self, "initial_healthy", healthy))
            total_dose = float(getattr(self, "total_dose", dose))
            reward = terminal_reward_kd(True, init_h, healthy, total_dose)
        else:
            # Terminal unsuccessful (or truncated-only path won't hit here): -1
            reward = -1.0 if terminated else 0.0

        # Provide all flags and counters in info for downstream logic/analysis
        info = {
            "successful": successful,
            "unsuccessful": unsuccessful,
            "timeout": timeout,
            "elapsed_hours": self.elapsed_hours,
        }

        # Update previous counts for next step
        self.prev_counts = (healthy, cancer)
        return observation, reward, terminated, truncated, info

    def close(self):
        """Release resources and perform any necessary cleanup."""
        # TODO: implement close logic
        pass

    def growth(self, num_hour, divisor1, divisor2, data_tab_growth):
        """Growth of the cellular environment before irradiation"""
    
        intervals1 = self.ctrl.get_intervals(num_hour, divisor1)
        intervals2 = self.ctrl.get_intervals(num_hour, divisor2)
    
        print("\nPERFORM TUMOR GROWTH SIMULATION")
        file_names = [f"t{t}_gd.txt" for t in intervals1]
        for hour in range(num_hour + 1):
            if hour in intervals1:
                self.ctrl.temp_data_tab()
            if hour in intervals2:
                self.ctrl.temp_cell_counts()
            self.ctrl.go()

        # Save growth results
        self.ctrl.save_data_tab(str(data_tab_growth), file_names, intervals1, len(intervals1))
        self.ctrl.save_cell_counts(str(data_tab_growth.parent.parent / "cell_num"), "cell_counts_gr.txt")

        # Save a copy of the grid
        self.ctrl.grid_copy = self.ctrl.grid
