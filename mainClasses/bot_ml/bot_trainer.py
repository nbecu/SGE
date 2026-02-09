import random
from collections import deque
import numpy as np


def build_dense_q_model(input_size, output_size, learning_rate=0.0005, hidden_sizes=(64, 64)):
    try:
        import tensorflow as tf
        from tensorflow import keras
    except Exception as exc:
        raise ImportError("TensorFlow/Keras is required for training.") from exc

    layers = [keras.layers.Input(shape=(input_size,))]
    for size in hidden_sizes:
        layers.append(keras.layers.Dense(size, activation="relu"))
    layers.append(keras.layers.Dense(output_size, activation="linear"))

    model = keras.Sequential(layers)
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), loss="mse")
    return model


class DQNTrainer:
    def __init__(
        self,
        policy_model,
        target_model,
        gamma=0.95,
        batch_size=128,
        target_update_steps=200,
        replay_maxlen=20000,
    ):
        self.policy_model = policy_model
        self.target_model = target_model
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_steps = target_update_steps
        self.replay_buffer = deque(maxlen=replay_maxlen)
        self.train_steps = 0

    def remember(self, obs, action_idx, reward, next_obs, done):
        self.replay_buffer.append((obs, action_idx, reward, next_obs, done))

    def train_from_replay(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        batch = random.sample(self.replay_buffer, self.batch_size)
        obs_batch = np.array([b[0] for b in batch], dtype=np.float32)
        next_obs_batch = np.array([b[3] for b in batch], dtype=np.float32)
        q_current = self.policy_model.predict(obs_batch, verbose=0)
        q_next_policy = self.policy_model.predict(next_obs_batch, verbose=0)
        q_next_target = self.target_model.predict(next_obs_batch, verbose=0)
        best_actions = np.argmax(q_next_policy, axis=1)
        for i, (_, action_idx, reward, _, done) in enumerate(batch):
            if done:
                q_current[i, action_idx] = reward
            else:
                q_current[i, action_idx] = reward + self.gamma * float(q_next_target[i, best_actions[i]])
        self.policy_model.fit(obs_batch, q_current, verbose=0)
        self.train_steps += 1
        if self.train_steps % self.target_update_steps == 0:
            self.target_model.set_weights(self.policy_model.get_weights())
