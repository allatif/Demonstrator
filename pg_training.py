import os
import json

import tensorflow as tf
from tensorflow import keras
import gym

from data.components.rl import environment as env
from data.components.rl.pg_util import *


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


n_inputs = 4
model = keras.models.Sequential([
    keras.layers.Dense(5, activation="elu", input_shape=[n_inputs]),
    keras.layers.Dense(1, activation="sigmoid"),
])


# env = env.Environment()
# obs = env.reset()

env = gym.make("CartPole-v1")
obs = env.reset()

n_iterations = 150
n_eps_per_update = 10
n_max_steps = 200
discount_factor = 0.95

optimizer = keras.optimizers.Adam(lr=0.01)
loss_fn = keras.losses.binary_crossentropy

total_reward_progress = []
smash_counter = 0
for iteration in range(n_iterations):
    all_rewards, all_grads = play_multiple_episodes(
        env, n_eps_per_update, n_max_steps, model, loss_fn, gym=True
    )
    all_final_rewards = discount_and_normalize_rewards(all_rewards,
                                                       discount_factor)

    flat_all_rewards = [i for ep_rewards in all_rewards for i in ep_rewards]
    total_iter_reward = float(sum(flat_all_rewards))
    total_reward_progress.append(total_iter_reward)

    all_mean_grads = []
    for var_index in range(len(model.trainable_variables)):
        mean_grads = tf.reduce_mean(
            [final_reward * all_grads[episode_index][step][var_index]
             for episode_index, final_rewards in enumerate(all_final_rewards)
             for step, final_reward in enumerate(final_rewards)], axis=0)
        all_mean_grads.append(mean_grads)
    optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))

    if total_iter_reward >= n_max_steps*n_eps_per_update - 1:
        smash_counter += 1

    print(f'done iter {iteration+1} of {n_iterations} \
          - r[{total_iter_reward}] ({smash_counter})')

    if smash_counter > 4:
        break


jsondumb = total_reward_progress

modelname = f'pg_ag10k_s{n_max_steps}_eps{n_eps_per_update}_i{n_iterations}'
if smash_counter > 0:
    modelname = modelname + f'({smash_counter})'

print('conserving plot data to json')
with open(f"tools\\conserved_plots\\{modelname}.json", 'w') as f:
    json.dump(jsondumb, f)

print('saving model:', modelname)
model.save(f"{modelname}.h5")
