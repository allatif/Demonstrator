import os

import tensorflow as tf
import numpy as np


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def play_one_step(env, obs, model, loss_fn, gym=False):
    with tf.GradientTape() as tape:
        left_proba = model(obs[np.newaxis])
        action = (tf.random.uniform([1, 1]) > left_proba)
        y_target = tf.constant([[1.]]) - tf.cast(action, tf.float32)
        loss = tf.reduce_mean(loss_fn(y_target, left_proba))
    grads = tape.gradient(loss, model.trainable_variables)
    if gym:
        obs, reward, done, info = env.step(int(action[0, 0].numpy()))
    else:
        obs, reward, done = env.step(int(action[0, 0].numpy()))
    return obs, reward, done, grads


def play_multiple_episodes(env, n_eps, n_max_steps, model, loss_fn, gym=False):
    all_rewards = []
    all_grads = []
    ep_rewards = []
    for ep in range(n_eps):
        current_rewards = []
        current_grads = []
        obs = env.reset()
        for step in range(n_max_steps):
            obs, reward, done, grads = play_one_step(env, obs, model,
                                                     loss_fn, gym)
            current_rewards.append(reward)
            current_grads.append(grads)
            if done:
                break

        all_rewards.append(current_rewards)
        all_grads.append(current_grads)
        ep_rewards.append(sum(current_rewards))

    best_ep_reward = max(ep_rewards)[0]
    return all_rewards, all_grads, best_ep_reward


def discount_rewards(rewards, discount_factor):
    discounted = np.array(rewards)
    for step in range(len(rewards) - 2, -1, -1):
        discounted[step] += discounted[step + 1] * discount_factor
    return discounted


def discount_and_normalize_rewards(all_rewards, discount_factor):
    all_discounted_rewards = [discount_rewards(rewards, discount_factor)
                              for rewards in all_rewards]
    flat_rewards = np.concatenate(all_discounted_rewards)
    reward_mean = flat_rewards.mean()
    reward_std = flat_rewards.std()  # + 1e-9
    # print("std:", reward_std)
    return [(discount_rewards - reward_mean) / reward_std
            for discount_rewards in all_discounted_rewards]
