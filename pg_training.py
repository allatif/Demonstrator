import os
import json

import tensorflow as tf
from tensorflow import keras
import gym

from data.components.rl import environment as env
from data.components.rl.pg_util import *


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


n_inputs = 5
model = keras.models.Sequential([
    keras.layers.Dense(8, activation="elu", input_shape=[n_inputs]),
    keras.layers.Dense(6, activation="elu"),
    keras.layers.Dense(6, activation="elu"),
    # keras.layers.Dense(6, activation="elu"),
    keras.layers.Dense(1, activation="sigmoid"),
])


env = env.Environment(adv_reward=True, ref=True)
obs = env.reset()

# env = gym.make("CartPole-v1")
# obs = env.reset()

n_iterations = 600
n_eps_per_update = 25
n_max_steps = 200
discount_factor = 0.99

optimizer = keras.optimizers.Adam(lr=0.01)
loss_fn = keras.losses.binary_crossentropy

total_reward_progress = []
i = 0
smash_counter = 0
best_score = n_max_steps*n_eps_per_update*0.85
for iteration in range(n_iterations):
    all_rewards, all_grads, best_ep_reward = play_multiple_episodes(
        env, n_eps_per_update, n_max_steps, model, loss_fn, gym=False
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
    i += 1

    if total_iter_reward > best_score:
        print('<good score, keeping weights>')
        best_weights = model.get_weights()
        best_score = total_iter_reward

    # total_iter_reward > 1750:
    if total_iter_reward > n_max_steps*n_eps_per_update*0.92:  # 0.88
        # if total_iter_reward > n_max_steps*n_eps_per_update - 1:
        smash_counter += 1

    print(f'done iter {iteration+1} of {n_iterations} \
          - r[{total_iter_reward}](bestep:{best_ep_reward}) \
          <best:{best_score}> ({smash_counter})')

    if smash_counter > 3:
        break


jsondumb = total_reward_progress

modelname = f'pg_refplus_R751e2_5866_spf50_g{int(discount_factor*100)}' \
            + f'_ag10k_s{n_max_steps}_eps{n_eps_per_update}_i{i}'

if smash_counter > 0:
    modelname = modelname + f'({smash_counter})'

model.set_weights(best_weights)

print('conserving plot data to json')
with open(f"tools\\conserved_plots\\{modelname}.json", 'w') as f:
    json.dump(jsondumb, f)

print('saving model:', modelname)
model.save(f"{modelname}.h5")
