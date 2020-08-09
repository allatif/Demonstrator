import os

from collections import deque

import numpy as np


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


replay_buffer = deque(maxlen=2000)


def epsilon_greedy_policy(state, model, epsilon=0):
    if np.random.rand() < epsilon:
        return np.random.randint(2)
    else:
        Q_values = model.predict(state[np.newaxis])
        return np.argmax(Q_values[0])


def sample_experiences(batch_size):
    indices = np.random.randint(len(replay_buffer), size=batch_size)
    batch = [replay_buffer[index] for index in indices]
    states, actions, rewards, next_states, dones = [
        np.array([experience[field_index] for experience in batch])
        for field_index in range(5)
    ]
    return states, actions, rewards, next_states, dones


def play_one_step(env, state, model, epsilon, gym=False):
    action = epsilon_greedy_policy(state, model, epsilon)
    if gym:
        next_state, reward, done, info = env.step(action)
    else:
        next_state, reward, done = env.step(action)
    replay_buffer.append((state, action, reward, next_state, done))
    return next_state, reward, done
