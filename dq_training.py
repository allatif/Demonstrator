import os
import json

import tensorflow as tf
from tensorflow import keras
# from tensorflow.keras import backend as K
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
    keras.layers.Dense(24, activation="elu"),
    keras.layers.Dense(n_outputs),
])

env = env.Environment(adv_reward=False)
obs = env.reset()

# env = gym.make("CartPole-v0")
# obs = env.reset()

batch_size = 128
discount_factor = 0.99
n_max_steps = 200
ep_trainbegin = 200
max_eps = 1000

optimizer = keras.optimizers.Adam(lr=1e-3)
loss_fn = keras.losses.mean_squared_error


def training_step(batch_size):
    experiences = sample_experiences(batch_size)
    states, actions, rewards, next_states, dones = experiences
    next_Q_values = model.predict(next_states)
    max_next_Q_values = np.max(next_Q_values, axis=1)
    target_Q_values = (rewards
                       + (1 - dones)*discount_factor*max_next_Q_values)
    target_Q_values = target_Q_values.reshape(-1, 1)
    mask = tf.one_hot(actions, n_outputs)
    with tf.GradientTape() as tape:
        all_Q_values = model(states)
        Q_values = tf.reduce_sum(all_Q_values*mask, axis=1, keepdims=True)
        loss = tf.reduce_mean(loss_fn(target_Q_values, Q_values))
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))


# env.seed(42)
# np.random.seed(42)
# tf.random.set_seed(42)

episode_reward_progress = []
best_score = 0
for episode in range(max_eps):
    # new_lr = (1 - episode/500, 0.0001)
    # K.set_value(model.optimizer.learning_rate, new_lr)
    obs = env.reset()

    episode_rewards = []
    for step in range(n_max_steps):
        epsilon = 1 if episode < 200 else max(epsilon*0.9997, 0.01)
        obs, reward, done = play_one_step(env, obs, model, epsilon, gym=False)
        episode_rewards.append(reward)
        if done:
            break

    episode_total_reward = round(np.float(sum(episode_rewards)), 2)
    episode_reward_progress.append(episode_total_reward)
    if episode_total_reward > best_score:
        best_weights = model.get_weights()
        best_score = episode_total_reward
    print(f'done episode {episode+1} of {max_eps} e={epsilon}'
          + f'- r[{episode_total_reward}]({best_score})')

    if episode > ep_trainbegin:
        training_step(batch_size)

jsondumb = episode_reward_progress

model.set_weights(best_weights)
modelname = f'deepq3216_b{batch_size}_s{n_max_steps}_ep{max_eps}' \
    + f'({ep_trainbegin})_sc{int(best_score)}'


print('conserving plot data to json')
with open(f"tools\\conserved_plots\\{modelname}.json", 'w') as f:
    json.dump(jsondumb, f)

print('saving model:', modelname)
model.save(f"{modelname}.h5")
