import random
from collections import deque
from pathlib import Path

import numpy as np


def _build_model():
    try:
        import tensorflow as tf
        from tensorflow import keras
    except Exception as exc:
        raise ImportError("TensorFlow/Keras is required for this mini test.") from exc

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(9,)),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(9, activation="linear"),
        ]
    )
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")
    return model


class MiniTicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [0] * 9  # 0 empty, 1 X, -1 O
        self.current = 1
        return self._obs()

    def _obs(self):
        return np.array(self.board, dtype=np.float32)

    def _lines(self):
        return [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

    def winner(self):
        for a, b, c in self._lines():
            if self.board[a] == self.board[b] == self.board[c] != 0:
                return self.board[a]
        return 0

    def is_draw(self):
        return all(v != 0 for v in self.board) and self.winner() == 0

    def valid_actions(self):
        return [i for i, v in enumerate(self.board) if v == 0]

    def step(self, action):
        if self.board[action] != 0:
            return self._obs(), -1.0, True
        self.board[action] = self.current
        win = self.winner()
        if win != 0:
            return self._obs(), 1.0, True
        if self.is_draw():
            return self._obs(), 0.2, True
        self.current *= -1
        return self._obs(), -0.02, False


def train_dqn(episodes=1000, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.98, gamma=0.9, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    env = MiniTicTacToe()
    policy = _build_model()
    target = _build_model()
    target.set_weights(policy.get_weights())

    buffer = deque(maxlen=5000)
    batch_size = 64
    target_update_steps = 200
    train_steps = 0

    def remember(s, a, r, s2, done):
        buffer.append((s, a, r, s2, done))

    def train_from_replay():
        nonlocal train_steps
        if len(buffer) < batch_size:
            return
        batch = random.sample(buffer, batch_size)
        s = np.array([b[0] for b in batch], dtype=np.float32)
        s2 = np.array([b[3] for b in batch], dtype=np.float32)
        q = policy.predict(s, verbose=0)
        q_next = target.predict(s2, verbose=0)
        for i, (_, a, r, _, done) in enumerate(batch):
            if done:
                q[i, a] = r
            else:
                q[i, a] = r + gamma * float(np.max(q_next[i]))
        policy.fit(s, q, verbose=0)
        train_steps += 1
        if train_steps % target_update_steps == 0:
            target.set_weights(policy.get_weights())

    for _ in range(episodes):
        s = env.reset()
        done = False
        while not done:
            valid = env.valid_actions()
            if random.random() < epsilon:
                a = random.choice(valid)
            else:
                q_vals = policy.predict(s.reshape(1, -1), verbose=0)[0]
                a = max(valid, key=lambda i: q_vals[i])

            s2, r, done = env.step(a)
            remember(s, a, r, s2, done)
            train_from_replay()

            if done:
                break

            # Opponent random move
            valid = env.valid_actions()
            if not valid:
                break
            a2 = random.choice(valid)
            s2, r2, done = env.step(a2)
            remember(s, a, r2, s2, done)
            train_from_replay()

            s = s2

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return policy


def quick_eval(policy, games=50):
    env = MiniTicTacToe()
    wins = 0
    losses = 0
    draws = 0
    for _ in range(games):
        s = env.reset()
        done = False
        while not done:
            valid = env.valid_actions()
            q_vals = policy.predict(s.reshape(1, -1), verbose=0)[0]
            a = max(valid, key=lambda i: q_vals[i])
            s, r, done = env.step(a)
            if done:
                if r > 0:
                    wins += 1
                elif r < 0:
                    losses += 1
                else:
                    draws += 1
                break
            valid = env.valid_actions()
            if not valid:
                draws += 1
                break
            a2 = random.choice(valid)
            s, r, done = env.step(a2)
            if done:
                if r < 0:
                    losses += 1
                elif r > 0:
                    wins += 1
                else:
                    draws += 1
    print(f"Eval over {games} games -> wins={wins}, losses={losses}, draws={draws}")


if __name__ == "__main__":
    model = train_dqn(episodes=1000)
    quick_eval(model, games=50)
