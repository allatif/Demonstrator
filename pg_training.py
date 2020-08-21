import os
import json
import argparse

import tensorflow as tf
from tensorflow import keras
import gym

from data.components.rl import environment as env_
from data.components.rl.pg_util import *


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def argparser():
    parser = argparse.ArgumentParser(
        description="############# Policy Gradient Training #############"
    )

    parser.add_argument("-x", "--inputs", metavar="",
                        help="number of inputs for ANN model",
                        type=int)

    parser.add_argument("-s", "--shape", nargs='+', metavar="",
                        help="list of the layer-density for ANN model")

    parser.add_argument("-i", "--iterations", metavar="",
                        help="number of training iterations, default: 600",
                        type=int)

    parser.add_argument("-e", "--episodes",
                        help="number of episodes per training step, \
                                default: 25",
                        type=int)

    parser.add_argument("-l", "--episode_length", metavar="",
                        help="length of episode, default: 200",
                        type=int)

    parser.add_argument("-v", "--variance", metavar="",
                        help="variance of initial state, default: 0 (low) \
                                options: 1 (med) and 2 (high)",
                        type=int)

    parser.add_argument("-g", "--gamma",
                        help="discount factor gamma, default: 0.99",
                        type=float)

    parser.add_argument("-a", "--adv_reward",
                        help="use environment with advanced reward function",
                        action="store_true")

    parser.add_argument("-r", "--reference",
                        help="use environment with reference system",
                        action="store_true")

    parser.add_argument("-y", "--openai_gym",
                        help="uses CartPole Gym environment",
                        action="store_true")

    return parser.parse_args()


def get_ann(inputs=4, shape=[5]):
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(shape[0], activation='elu',
                                 input_shape=[inputs]))
    if len(shape) > 1:
        for den in shape[1:]:
            model.add(keras.layers.Dense(den, activation="elu"))

    model.add(keras.layers.Dense(1, activation="sigmoid"))

    return model


def main():
    args = argparser()

    if not args.openai_gym:
        model = get_ann(inputs=args.inputs, shape=args.shape)

    variance = 0
    if args.variance is not None:
        variance = args.variance
    env = env_.Environment(adv_reward=args.adv_reward, ref=args.reference,
                           variance=variance)
    obs = env.reset()

    if args.openai_gym:
        model = get_ann()
        env = gym.make("CartPole-v1")
        obs = env.reset()

    # number of training iterations
    n_iterations = 600
    if args.iterations is not None:
        n_iterations = args.iterations

    # number of episodes per training step
    n_eps_per_update = 25
    if args.episodes is not None:
        n_eps_per_update = args.episodes

    # length of episode
    n_max_steps = 200
    if args.episode_length is not None:
        n_max_steps = args.episode_length

    # discount factor (gamma)
    discount_factor = 0.99
    if args.gamma is not None:
        discount_factor = args.gamma

    if args.openai_gym:
        # OpenAI Gym setup
        n_iterations = 150
        n_eps_per_update = 10
        n_max_steps = 200
        discount_factor = 0.95

    treshhold_factor = 0.9995
    if args.variance == 0:
        treshhold_factor = 0.94
    elif args.variance == 1:
        treshhold_factor = 0.90
    elif args.variance == 2:
        treshhold_factor = 0.80

    optimizer = keras.optimizers.Adam(lr=0.01)
    loss_fn = keras.losses.binary_crossentropy

    total_reward_progress = []
    i = 0
    smash_counter = 0
    best_score = n_max_steps*n_eps_per_update*treshhold_factor*0.90
    best_weights = None
    for iteration in range(n_iterations):
        all_rewards, all_grads, best_ep_reward = play_multiple_episodes(
            env, n_eps_per_update, n_max_steps, model, loss_fn,
            gym=args.openai_gym
        )
        all_final_rewards = discount_and_normalize_rewards(all_rewards,
                                                           discount_factor)

        flat_all_rewards = [i for ep_rewards in all_rewards for i in ep_rewards]
        total_iter_reward = float(sum(flat_all_rewards))
        total_reward_progress.append(total_iter_reward)

        all_mean_grads = []
        for var_index in range(len(model.trainable_variables)):
            mean_grads = tf.reduce_mean(
                [final_reward * all_grads[ep_index][step][var_index]
                 for ep_index, final_rewards in enumerate(all_final_rewards)
                 for step, final_reward in enumerate(final_rewards)], axis=0)
            all_mean_grads.append(mean_grads)
        optimizer.apply_gradients(
            zip(all_mean_grads, model.trainable_variables)
        )
        i += 1

        if total_iter_reward > best_score:
            print('< < best score, keeping weights > >')
            best_weights = model.get_weights()
            best_score = total_iter_reward

        if total_iter_reward > n_max_steps*n_eps_per_update*treshhold_factor:
            smash_counter += 1

        print(f'done iter {iteration+1} of {n_iterations} \
              - G_t={total_iter_reward} (G_best_ep: {best_ep_reward}) \
              <score: {best_score}> ({smash_counter})')

        if smash_counter > 5:
            break

    jsondumb = total_reward_progress

    if args.variance == 0:
        v_str = 'low'
    elif args.variance == 1:
        v_str = 'med'
    elif args.variance == 2:
        v_str = 'high'

    if args.openai_gym:
        inputs_str = '4'
        annshape_str = '5'
    else:
        inputs_str = args.inputs
        annshape_str = ''.join(args.shape)
    modelname = f'pg_{v_str}_ref{int(args.reference)}_R{int(args.adv_reward)}' \
                + f'_{inputs_str}{annshape_str}_g{int(discount_factor*100)}' \
                + f'_s{n_max_steps}_eps{n_eps_per_update}_i{i}'
    if args.openai_gym:
        modelname = f'pg_CartPole_{inputs_str}{annshape_str}_i{i}'

    if smash_counter > 0:
        modelname = modelname + f'({smash_counter})'

    if best_weights is not None:
        model.set_weights(best_weights)

    print('conserving plot data to json')
    with open(f"tools\\conserved_plots\\{modelname}.json", 'w') as f:
        json.dump(jsondumb, f)

    print('saving model:', modelname)
    model.save(f"{modelname}.h5")


if __name__ == '__main__':
    main()
