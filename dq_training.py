import os
import json

import tensorflow as tf
from tensorflow import keras
import gym

from data.components.rl import environment as env
from data.components.rl.dq_util import *


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


input_shape = [4]
n_outputs = 2
model = keras.models.Sequential([
    keras.layers.Dense(32, activation="elu", input_shape=input_shape),
    keras.layers.Dense(32, activation="elu"),
    keras.layers.Dense(n_outputs),
])

# env = env.Environment()
# obs = env.reset()

env = gym.make("CartPole-v1")
obs = env.reset()

batch_size = 32
discount_factor = 0.95
n_max_steps = 200
max_eps = 600

optimizer = keras.optimizers.Adam(lr=1e-3)
loss_fn = keras.losses.mean_squared_error


def training_step(batch_size):
    experiences = sample_experiences(batch_size)
    states, actions, rewards, next_states, dones = experiences
    next_Q_values = model.predict(next_states)
    max_next_Q_values = np.max(next_Q_values, axis=1)
    target_Q_values = (rewards
                       + (1 - dones)*discount_factor*max_next_Q_values)
    mask = tf.one_hot(actions, n_outputs)
    with tf.GradientTape() as tape:
        all_Q_values = model(states)
        Q_values = tf.reduce_sum(all_Q_values*mask, axis=1, keepdims=True)
        loss = tf.reduce_mean(loss_fn(target_Q_values, Q_values))
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))


episode_reward_progress = []
for episode in range(max_eps):
    obs = env.reset()

    episode_rewards = []
    for step in range(n_max_steps):
        epsilon = max(1 - episode/500, 0.01)
        obs, reward, done = play_one_step(env, obs, model, epsilon, gym=True)
        episode_rewards.append(reward)
        if done:
            break

    episode_total_reward = sum(episode_rewards)
    print(f'done episode {episode+1} of {max_eps} - r[{episode_total_reward}]')
    episode_reward_progress.append(episode_total_reward)

    if episode > 50:
        training_step(batch_size)

jsondumb = episode_reward_progress


modelname = f'deepq_cartpole_s{n_max_steps}_ep{max_eps}'

print('conserving plot data to json')
with open(f"tools\\conserved_plots\\{modelname}.json", 'w') as f:
    json.dump(jsondumb, f)

print('saving model:', modelname)
model.save(f"{modelname}.h5")
