"""Training entry-point for the DQN agent on the `CellSimEnv` environment."""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch

from .dqn_agent import DQNAgent, DQNConfig
from .rl_env import CellSimEnv


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the training script."""
    parser = argparse.ArgumentParser(description="Train a DQN agent for CellSimEnv")
    parser.add_argument("--episodes", type=int, default=500, help="Numero di episodi di training")
    parser.add_argument("--max-steps", type=int, default=1_000, help="Numero massimo di step per episodio")
    parser.add_argument("--seed", type=int, default=0, help="Seed di inizializzazione")
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=("cpu", "cuda", "auto"),
        help="Dispositivo da usare (predefinito CPU). USA 'auto' per preferire CUDA se disponibile",
    )
    parser.add_argument("--dose-bins", type=int, default=5, help="Numero di discretizzazioni per la dose")
    parser.add_argument("--wait-bins", type=int, default=6, help="Numero di discretizzazioni per il tempo di attesa")
    parser.add_argument("--gamma", type=float, default=0.99, help="Sconto futuro gamma")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate per l'ottimizzatore")
    parser.add_argument("--batch-size", type=int, default=64, help="Dimensione dei mini-batch")
    parser.add_argument("--buffer-size", type=int, default=100_000, help="Capacità dell'esperience replay")
    parser.add_argument(
        "--warmup-steps",
        type=int,
        default=5_000,
        help="Numero minimo di transizioni nel buffer prima dell'aggiornamento",
    )
    parser.add_argument("--target-update", type=int, default=1_000, help="Intervallo di aggiornamento della rete target")
    parser.add_argument("--epsilon-start", type=float, default=1.0, help="Valore iniziale di epsilon")
    parser.add_argument("--epsilon-end", type=float, default=0.05, help="Valore minimo di epsilon")
    parser.add_argument(
        "--epsilon-decay-steps",
        type=int,
        default=100_000,
        help="Numero di step per la decrescita lineare di epsilon",
    )
    parser.add_argument(
        "--eval-episodes",
        type=int,
        default=5,
        help="Numero di episodi da giocare in valutazione greedy al termine del training",
    )
    parser.add_argument(
        "--save-path",
        type=Path,
        default=Path("results/dqn_agent.pt"),
        help="Percorso dove salvare i pesi dell'agente",
    )
    return parser.parse_args()


def resolve_device(device_flag: str) -> torch.device:
    """Return the torch.device matching the CLI flag, defaulting to CPU."""
    if device_flag == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    if device_flag == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def seed_everything(seed: int) -> None:
    """Make the run deterministic as much as possible."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_discrete_actions(
    action_space,
    dose_bins: int,
    wait_bins: int,
) -> List[np.ndarray]:
    """Discretise the continuous action space into a finite grid for DQN."""
    dose_values = np.linspace(float(action_space.low[0]), float(action_space.high[0]), num=dose_bins)
    wait_values = np.linspace(float(action_space.low[1]), float(action_space.high[1]), num=wait_bins)
    actions: List[np.ndarray] = []
    for dose in dose_values:
        for wait in wait_values:
            actions.append(np.asarray([dose, wait], dtype=np.float32))
    return actions


def linear_epsilon(step: int, start: float, end: float, decay_steps: int) -> float:
    """Linearly anneal epsilon from start to end across decay_steps."""
    if decay_steps <= 0:
        return end
    fraction = min(1.0, step / float(decay_steps))
    return start + fraction * (end - start)


def evaluate_policy(agent: DQNAgent, env: CellSimEnv, episodes: int, max_steps: int) -> Tuple[float, float]:
    """Play episodes with greedy policy and collect stats (mean reward, success rate)."""
    rewards = []
    successes = 0
    for ep in range(episodes):
        state, _ = env.reset()
        episode_reward = 0.0
        for _ in range(max_steps):
            action_idx, action = agent.select_action(state, epsilon=0.0)
            next_state, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            state = next_state
            if terminated or truncated:
                if info.get("successful", False):
                    successes += 1
                break
        rewards.append(episode_reward)
    mean_reward = float(np.mean(rewards)) if rewards else 0.0
    success_rate = successes / max(1, episodes)
    return mean_reward, success_rate


def main() -> None:
    """Run the full DQN training loop and optional evaluation."""
    args = parse_args()
    device = resolve_device(args.device)
    seed_everything(args.seed)

    env = CellSimEnv()
    discrete_actions = build_discrete_actions(env.action_space, args.dose_bins, args.wait_bins)
    state_dim = int(np.prod(env.observation_space.shape))

    config = DQNConfig(
        gamma=args.gamma,
        learning_rate=args.lr,
        batch_size=args.batch_size,
        buffer_size=args.buffer_size,
        min_buffer_size=args.warmup_steps,
        target_update_interval=args.target_update,
    )
    agent = DQNAgent(state_dim, discrete_actions, device, config)

    total_steps = 0
    episode_rewards: List[float] = []
    losses: List[float] = []

    for episode in range(1, args.episodes + 1):
        state, _ = env.reset(seed=args.seed + episode)
        episode_reward = 0.0
        info = {}

        for _ in range(args.max_steps):
            current_epsilon = linear_epsilon(total_steps, args.epsilon_start, args.epsilon_end, args.epsilon_decay_steps)
            action_idx, action = agent.select_action(state, current_epsilon)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            agent.store_transition(state, action_idx, reward, next_state, done)

            loss = agent.update()
            if loss is not None:
                losses.append(loss)

            state = next_state
            episode_reward += reward
            total_steps += 1

            if done:
                break

        episode_rewards.append(episode_reward)
        info_str = "success" if info.get("successful", False) else "timeout" if info.get("timeout", False) else "failure"
        avg_reward = np.mean(episode_rewards[-10:])
        avg_loss = np.mean(losses[-10:]) if losses else math.nan
        print(
            f"Episode {episode:04d} | steps: {total_steps:06d} | reward: {episode_reward:.3f} | "
            f"avg10 reward: {avg_reward:.3f} | avg10 loss: {avg_loss:.5f} | eps: {current_epsilon:.3f} | {info_str}"
        )

    args.save_path.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(args.save_path))
    print(f"Modello salvato in {args.save_path}")

    if args.eval_episodes > 0:
        mean_reward, success_rate = evaluate_policy(agent, env, args.eval_episodes, args.max_steps)
        print(
            f"Valutazione finale -> reward media: {mean_reward:.3f}, tasso di successo: {success_rate:.2%}"
        )

    env.close()


if __name__ == "__main__":
    main()
