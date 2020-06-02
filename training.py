import os

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt

from data.components.rl import environment as env
from data.components import colors
from data.components.rl.util import *


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


n_inputs = 4
model = keras.models.Sequential([
    keras.layers.Dense(5, activation="elu", input_shape=[n_inputs]),
    keras.layers.Dense(1, activation="sigmoid"),
])


env = env.Environment()
obs = env.reset()

n_iterations = 750
n_eps_per_update = 10
n_max_steps = 500
discount_factor = 0.95

optimizer = keras.optimizers.Adam(lr=0.01)
loss_fn = keras.losses.binary_crossentropy


loss_progress = []
total_reward_progress = []
for iteration in range(n_iterations):
    print("start iter", iteration+1, "of total", n_iterations)

    all_rewards, all_grads, total_loss = play_multiple_episodes(
        env, n_eps_per_update, n_max_steps, model, loss_fn
    )
    all_final_rewards = discount_and_normalize_rewards(all_rewards,
                                                       discount_factor)

    loss_progress.append(total_loss)

    flatten_all_rewards = [i for ep_rewards in all_rewards for i in ep_rewards]
    total_reward_progress.append(sum(flatten_all_rewards))

    all_mean_grads = []
    for var_index in range(len(model.trainable_variables)):
        mean_grads = tf.reduce_mean(
            [final_reward * all_grads[episode_index][step][var_index]
             for episode_index, final_rewards in enumerate(all_final_rewards)
             for step, final_reward in enumerate(final_rewards)], axis=0)
        all_mean_grads.append(mean_grads)

    optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))


modelname = 'pg_r2_ang20_env15_500_i750'

print('saving model')
model.save(f"{modelname}.h5")


# Plot Loss and rewards
print('plotting loss and rewards')
plt.figure(figsize=(12, 8), dpi=80, facecolor=(colors.get_pp(colors.WHITE)))

plt.subplot(211)
plt.plot(loss_progress, color=colors.get_pp(colors.LBLUE))
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.grid(True)

plt.subplot(212)
plt.plot(total_reward_progress, color=colors.get_pp(colors.TOMATO))
plt.xlabel('Iterations')
plt.ylabel('Total Rewards')
plt.grid(True)

print('saving plot')
plt.savefig(f"{modelname}.png")
