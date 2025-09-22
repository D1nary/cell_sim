from __future__ import annotations

import math
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import torch
import torch.nn.utils as nn_utils

from .config import PPOConfig
from .models import ActorCritic
from .storage import RolloutBuffer
from .utils import format_metrics

try:
    from gymnasium import Env
except ImportError:  # pragma: no cover
    Env = object  # type: ignore


class PPOAgent:
    """On-policy PPO agent handling data collection and updates."""

    def __init__(
        self,
        env: Env,
        config: PPOConfig,
        device: torch.device,
        env_factory: Optional[Callable[[], Env]] = None,
    ) -> None:
        self.env = env
        self.config = config
        self.device = device
        self.env_factory = env_factory

        obs_space = env.observation_space
        action_space = env.action_space
        obs_dim = int(obs_space.shape[0])
        act_dim = int(action_space.shape[0])

        self.model = ActorCritic(obs_space, action_space, hidden_sizes=config.hidden_sizes).to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate, eps=1e-5)
        self.buffer = RolloutBuffer(config.rollout_steps, obs_dim, act_dim, device)

        self.global_step = 0
        self.last_log_step = 0
        self.last_eval_step = 0
        self.episode_returns: deque[float] = deque(maxlen=100)
        self.episode_lengths: deque[int] = deque(maxlen=100)
        self.success_counter = 0
        self.completed_episodes = 0

        # Initialise environment state
        obs, info = self.env.reset(seed=config.seed)
        self.current_obs = obs
        self.current_info = info
        self.last_done = False

    def collect_rollout(self) -> Dict[str, float]:
        cfg = self.config
        rollout_rewards = []
        rollout_lengths = []
        successes = 0
        failures = 0
        timeouts = 0

        episode_reward = 0.0
        episode_length = 0

        for _ in range(cfg.rollout_steps):
            obs_tensor = torch.as_tensor(self.current_obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            with torch.no_grad():
                action_tensor, action_norm, log_prob, value = self.model.act(obs_tensor)
            action = action_tensor.cpu().numpy()[0]
            next_obs, reward, terminated, truncated, info = self.env.step(action)
            done = bool(terminated or truncated)

            self.buffer.add(
                obs_tensor.squeeze(0),
                action_norm.squeeze(0),
                log_prob.squeeze(0),
                float(reward),
                done,
                value.squeeze(0),
            )

            self.global_step += 1
            episode_reward += float(reward)
            episode_length += 1

            if done:
                rollout_rewards.append(episode_reward)
                rollout_lengths.append(episode_length)
                self.episode_returns.append(episode_reward)
                self.episode_lengths.append(episode_length)
                self.completed_episodes += 1
                if info.get("successful", False):
                    successes += 1
                    self.success_counter += 1
                if info.get("unsuccessful", False):
                    failures += 1
                if info.get("timeout", False):
                    timeouts += 1
                next_obs, info = self.env.reset()
                episode_reward = 0.0
                episode_length = 0

            self.current_obs = next_obs
            self.current_info = info
            self.last_done = done

        with torch.no_grad():
            obs_tensor = torch.as_tensor(self.current_obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            next_value = self.model.evaluate_value(obs_tensor).squeeze(0)
        if self.last_done:
            next_value = torch.zeros_like(next_value)

        self.buffer.compute_returns_and_advantages(next_value, self.last_done, cfg.gamma, cfg.gae_lambda)

        mean_reward = float(np.mean(rollout_rewards)) if rollout_rewards else 0.0
        mean_length = float(np.mean(rollout_lengths)) if rollout_lengths else 0.0
        success_rate = successes / max(1, len(rollout_rewards))

        return {
            "rollout_mean_reward": mean_reward,
            "rollout_mean_length": mean_length,
            "rollout_success_rate": success_rate,
            "rollout_episodes": float(len(rollout_rewards)),
            "rollout_failures": float(failures),
            "rollout_timeouts": float(timeouts),
        }

    def update(self) -> Dict[str, float]:
        cfg = self.config
        self.buffer.advantages = (self.buffer.advantages - self.buffer.advantages.mean()) / (
            self.buffer.advantages.std(unbiased=False) + 1e-8
        )

        total_pg_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        approx_kl = 0.0
        clip_frac = 0.0
        batches = 0

        for _ in range(cfg.update_epochs):
            for batch in self.buffer.iter_minibatches(cfg.minibatch_size):
                new_log_prob, entropy, new_values = self.model.evaluate_actions(batch.observations, batch.actions)
                log_ratio = new_log_prob - batch.log_probs
                ratio = log_ratio.exp()

                with torch.no_grad():
                    approx_kl += torch.mean((batch.log_probs - new_log_prob)).abs().item()
                    clip_frac += (
                        torch.gt(torch.abs(ratio - 1.0), cfg.clip_coef).float().mean().item()
                    )

                pg_loss_1 = -batch.advantages * ratio
                pg_loss_2 = -batch.advantages * torch.clamp(
                    ratio, 1.0 - cfg.clip_coef, 1.0 + cfg.clip_coef
                )
                pg_loss = torch.max(pg_loss_1, pg_loss_2).mean()

                value_pred = new_values
                value_pred_clipped = batch.values + (value_pred - batch.values).clamp(-cfg.clip_coef, cfg.clip_coef)
                value_losses_unclipped = (value_pred - batch.returns) ** 2
                value_losses_clipped = (value_pred_clipped - batch.returns) ** 2
                value_loss = 0.5 * torch.max(value_losses_unclipped, value_losses_clipped).mean()

                entropy_loss = entropy.mean()

                loss = pg_loss + cfg.value_coef * value_loss - cfg.entropy_coef * entropy_loss

                self.optimizer.zero_grad()
                loss.backward()
                nn_utils.clip_grad_norm_(self.model.parameters(), cfg.max_grad_norm)
                self.optimizer.step()

                total_pg_loss += pg_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy_loss.item()
                batches += 1

        self.buffer.reset()

        if batches > 0:
            total_pg_loss /= batches
            total_value_loss /= batches
            total_entropy /= batches
            approx_kl /= batches
            clip_frac /= batches

        return {
            "policy_loss": total_pg_loss,
            "value_loss": total_value_loss,
            "entropy": total_entropy,
            "approx_kl": approx_kl,
            "clip_fraction": clip_frac,
        }

    def evaluate(self) -> Dict[str, float]:
        cfg = self.config
        eval_env = self.env_factory() if self.env_factory else self.env
        close_env = self.env_factory is not None
        returns = []
        successes = 0

        try:
            for episode in range(cfg.num_eval_episodes):
                obs, info = eval_env.reset(seed=cfg.seed + episode)
                done = False
                total_reward = 0.0
                while not done:
                    obs_tensor = torch.as_tensor(
                        obs, dtype=torch.float32, device=self.device
                    ).unsqueeze(0)
                    with torch.no_grad():
                        action_tensor, _, _, _ = self.model.act(
                            obs_tensor, deterministic=True
                        )
                    action = action_tensor.cpu().numpy()[0]
                    obs, reward, terminated, truncated, info = eval_env.step(action)
                    total_reward += float(reward)
                    done = bool(terminated or truncated)
                returns.append(total_reward)
                if info.get("successful", False):
                    successes += 1
        finally:
            if close_env:
                eval_env.close()

        mean_return = float(np.mean(returns)) if returns else 0.0
        success_rate = successes / max(1, len(returns))
        return {"eval_return": mean_return, "eval_success_rate": success_rate}

    def maybe_log(self, rollout_stats: Dict[str, float], update_stats: Dict[str, float]) -> None:
        cfg = self.config
        should_log = (self.global_step - self.last_log_step) >= cfg.log_interval
        if not should_log:
            return
        self.last_log_step = self.global_step

        avg_return = float(np.mean(self.episode_returns)) if self.episode_returns else 0.0
        avg_length = float(np.mean(self.episode_lengths)) if self.episode_lengths else 0.0
        scalars = {
            "step": float(self.global_step),
            "avg_return": avg_return,
            "avg_length": avg_length,
        }
        scalars.update(rollout_stats)
        scalars.update(update_stats)
        print(f"[train] {format_metrics(scalars)}")

    def maybe_evaluate(self) -> Dict[str, float] | None:
        cfg = self.config
        should_eval = (self.global_step - self.last_eval_step) >= cfg.eval_interval
        if not should_eval:
            return None
        self.last_eval_step = self.global_step
        eval_stats = self.evaluate()
        print(f"[eval] {format_metrics(eval_stats)}")
        return eval_stats

    def train(self) -> Dict[str, float]:
        cfg = self.config
        best_success = -math.inf
        plateau_counter = 0
        final_eval: Dict[str, float] = {}

        while self.global_step < cfg.total_timesteps:
            rollout_stats = self.collect_rollout()
            update_stats = self.update()
            self.maybe_log(rollout_stats, update_stats)
            eval_stats = self.maybe_evaluate()
            if eval_stats:
                final_eval = eval_stats
                success_rate = eval_stats.get("eval_success_rate", 0.0)
                if success_rate > best_success:
                    best_success = success_rate
                    plateau_counter = 0
                    self.save_checkpoint(cfg.checkpoint_path)
                else:
                    plateau_counter += 1
                if success_rate >= cfg.target_success_rate and plateau_counter >= cfg.early_stop_patience:
                    print(
                        "[train] Early stopping triggered: success rate target maintained"
                    )
                    break

        if not final_eval:
            final_eval = self.evaluate()
        return final_eval

    def save_checkpoint(self, path: Path | str) -> None:
        checkpoint_path = Path(path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model_state_dict": self.model.state_dict()}, checkpoint_path)


__all__ = ["PPOAgent"]
