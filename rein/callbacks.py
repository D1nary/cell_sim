"""Callback stubs for training control.

These are optional hooks you can plug into the train loop to implement
early stopping or custom logging without changing the core logic.
"""
from __future__ import annotations

from dataclasses import dataclass


class Callback:
    def on_episode_end(self, *_args, **_kwargs) -> None:  # noqa: D401
        """Called at the end of each episode."""
        return None

    def should_stop(self) -> bool:
        return False


@dataclass
class StopOnSuccessRate(Callback):
    """Stop once success rate over a moving window reaches a threshold."""

    window: int = 10
    threshold: float = 0.9

    def __post_init__(self) -> None:
        self._history: list[bool] = []

    def on_episode_end(self, *, info: dict, **_kwargs) -> None:  # type: ignore[override]
        self._history.append(bool(info.get("successful", False)))
        if len(self._history) > self.window:
            self._history.pop(0)

    def should_stop(self) -> bool:  # type: ignore[override]
        if not self._history or len(self._history) < self.window:
            return False
        rate = sum(self._history) / float(len(self._history))
        return rate >= self.threshold


__all__ = [
    "Callback",
    "StopOnSuccessRate",
]

