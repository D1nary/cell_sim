"""Reinforcement learning environment for the cell simulator.

This module defines :class:`CellSimEnv`, a placeholder Gym-compatible
environment for controllin radiation treatment.
"""

from __future__ import annotations

import copy
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from rein import cell_sim
from rein.configs.defaults import DEFAULT_CONFIG

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
        max_dose: float = 5.0,
        max_wait: int = 24,
        min_dose: float = 0.0,
        min_wait: int = 0,
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
        min_dose : float
            Minimum radiation dose deliverable in a single step.
        max_wait : int
            Maximum number of hours to advance the simulation after dosing.
        min_wait : int
            Minimum number of hours to advance the simulation after dosing.
        """

        # super().__init__()

        # Environment starts open; used by close() idempotency
        self._closed: bool = False

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
        if min_dose > max_dose:
            raise ValueError("min_dose cannot be greater than max_dose")
        if min_wait > max_wait:
            raise ValueError("min_wait cannot be greater than max_wait")
        self.min_dose = float(min_dose)
        self.max_dose = float(max_dose)
        self.min_wait = int(min_wait)
        self.max_wait = int(max_wait)
        self.episode_timeout_hours = int(DEFAULT_CONFIG.episode_timeout_hours)

        # Tracks cumulative simulated hours to detect timeout
        self.elapsed_hours = 0
        self.action_space = spaces.Box(
            low=np.array([self.min_dose, float(self.min_wait)], dtype=np.float32),
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

        # Create a deep-copied snapshot of the current grid for resets
        self.reset_grid = copy.deepcopy(self.ctrl.grid)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        """Reset the simulator state and return initial observation.

        Actions performed:
        - Reset the controller's hour tick counter (`ctrl.tick = 0`).
        - Restore the grid snapshot with `ctrl.set_grid(self.reset_grid)`.
        - Clear controller temporary buffers (voxel and counts).
        - Reset environment bookkeeping (elapsed hours, dose, prev counts).
        - Optionally reseed RNG when ``seed`` is provided.

        Returns a tuple ``(observation, info)`` as per Gym API.
        """
        # Handle seeding for reproducibility
        if seed is not None:
            try:
                super().reset(seed=seed)
            except Exception:
                # Older Gym versions may not support super().reset(seed=...)
                pass
            try:
                # Seed the underlying C++ RNG as well (best-effort)
                cell_sim.seed(int(seed) & 0xFFFFFFFF)
            except Exception:
                pass

        # Restore simulator state
        try:
            # Reset simulated time and clear temp buffers
            self.ctrl.tick = 0
            if hasattr(self.ctrl, "clear_tempDataTab"):
                self.ctrl.clear_tempDataTab()
            if hasattr(self.ctrl, "clear_tempCellCounts"):
                self.ctrl.clear_tempCellCounts()

            # Restore the grid to the saved initial snapshot
            self.ctrl.set_grid(self.reset_grid)
        except Exception as e:
            # If anything goes wrong, surface a clear error
            raise RuntimeError(f"Failed to reset simulator: {e}")

        # Read fresh counts from the restored grid
        counts = self.ctrl.get_cell_counts()

        # Reset environment bookkeeping
        self.initial_healthy = float(counts[0])
        self.prev_counts = tuple(map(float, counts))
        self.elapsed_hours = 0
        self.total_dose = 0.0

        observation = np.asarray(counts, dtype=np.float32)
        info = {
            "successful": False,
            "unsuccessful": False,
            "timeout": False,
            "elapsed_hours": self.elapsed_hours,
            "total_dose": self.total_dose,
        }
        return observation, info

    def step(self, action):
        """Apply an action and advance the simulation."""
        # Action is (dose, wait_hours)
        a = np.asarray(action, dtype=np.float32)
        dose = float(np.clip(a[0], self.min_dose, self.max_dose))
        hours = int(np.clip(a[1], float(self.min_wait), float(self.max_wait)))

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
        _timeout = bool(self.elapsed_hours >= self.episode_timeout_hours)

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
            "total_dose": float(self.total_dose),
        }

        # Update previous counts for next step
        self.prev_counts = (healthy, cancer)
        return observation, reward, terminated, truncated, info

    def close(self):
        """Release resources and perform any necessary cleanup."""
        # Make close idempotent
        if getattr(self, "_closed", False):
            return

        # Best-effort cleanup of simulator buffers
        ctrl = getattr(self, "ctrl", None)
        if ctrl is not None:
            try:
                if hasattr(ctrl, "clear_tempDataTab"):
                    ctrl.clear_tempDataTab()
            except Exception:
                pass
            try:
                if hasattr(ctrl, "clear_tempCellCounts"):
                    ctrl.clear_tempCellCounts()
            except Exception:
                pass

        # Note: Do not set self.ctrl/reset_grid to None to avoid
        # Optional attribute warnings from static checkers (Pylance).
        # Actual resource release will occur when the env is GC'ed.

        # Mark as closed and defer to Gym's close (no-op in many versions)
        self._closed = True
        try:
            super().close()
        except Exception:
            pass

    # def growth(self, num_hour, divisor1, divisor2, data_tab_growth):
    def growth(self, num_hour):
        """Growth of the cellular environment before irradiation"""
    
        # intervals1 = self.ctrl.get_intervals(num_hour, divisor1)
        # intervals2 = self.ctrl.get_intervals(num_hour, divisor2)
    
        print("\nPERFORM TUMOR GROWTH SIMULATION")
        # file_names = [f"t{t}_gd.txt" for t in intervals1]
        for hour in range(num_hour + 1):
            # if hour in intervals1:
            #     self.ctrl.temp_data_tab()
            # if hour in intervals2:
            #     self.ctrl.temp_cell_counts()
            self.ctrl.go()

        # Save growth results
        # self.ctrl.save_data_tab(str(data_tab_growth), file_names, intervals1, len(intervals1))
        # self.ctrl.save_cell_counts(str(data_tab_growth.parent.parent / "cell_num"), "cell_counts_gr.txt")
