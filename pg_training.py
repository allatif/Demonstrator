import os
import json
import argparse

import tensorflow as tf
from tensorflow import keras
import gym

from data.components.rl import environment as env_
from data.components.rl.pg_util import *
from data.components.rl import model_ripper as rip


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

    parser.add_argument("-c", "--continue_", metavar="",
                        help="loads an old model and continue training",
                        type=str)

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

    hypers = {
        'iterations': 600,
        'episodes per iteration': 25,
        'steps per episode': 200,
        'discount': 0.99,
        'advanced reward': args.adv_reward,
        'reference': args.reference,
        'variance': 0
    }

    old_i = 0
    old_best = 0

    if not args.openai_gym and args.continue_ is None:
        model = get_ann(inputs=args.inputs, shape=args.shape)

    if args.continue_:
        model = keras.models.load_model(args.continue_, compile=False)
        ripped_hypers = rip.model_ripper(args.continue_)
        hypers['episodes per iteration'] = ripped_hypers['eps']
        hypers['steps per episode'] = ripped_hypers['s']
        hypers['discount'] = ripped_hypers['g']
        hypers['advanced reward'] = ripped_hypers['R']
        hypers['reference'] = ripped_hypers['ref']
        hypers['variance'] = ripped_hypers['var']
        hypers['info'] = ripped_hypers['info']

        old_i = ripped_hypers['i']
        old_best = ripped_hypers['Gt']

    # Overwrite hypers when args are passed
    if args.iterations is not None:
        hypers['iterations'] = args.iterations
    if args.episodes is not None:
        hypers['episodes per iteration'] = args.episodes
    if args.episode_length is not None:
        hypers['steps per episode'] = args.episode_length
    if args.gamma is not None:
        hypers['discount'] = args.gamma
    if args.variance is not None:
        hypers['variance'] = args.variance

    env = env_.Environment(adv_reward=hypers['advanced reward'],
                           ref=hypers['reference'],
                           variance=hypers['variance'])
    _ = env.reset()

    if args.openai_gym:
        model = get_ann()
        env = gym.make("CartPole-v1")
        _ = env.reset()

    # OpenAI Gym setup
    if args.openai_gym:
        hypers['iterations'] = 150
        hypers['episodes per iteration'] = 10
        hypers['steps per episode'] = 200
        hypers['discount'] = 0.95

    threshold_factor = 0.9995
    if hypers['variance'] == 0:
        threshold_factor = 0.94
    elif hypers['variance'] == 1:
        threshold_factor = 0.90
    elif hypers['variance'] == 2:
        threshold_factor = 0.60

    optimizer = keras.optimizers.Adam(lr=0.01)
    loss_fn = keras.losses.binary_crossentropy

    total_reward_progress = []
    smash_counter = 0

    total_steps = hypers['steps per episode'] * hypers['episodes per iteration']
    best_score = total_steps * threshold_factor * 0.90

    if args.continue_:
        best_score = old_best

    print('Start training ...')
    print('Using following hyperparameters:')
    for key, value in hypers.items():
        print(f'\t{key}: {value}')
    print('--------------------------------')

    i_best = 0
    best_weights = None
    for i in range(hypers['iterations']):
        all_rewards, all_grads, best_ep_reward = play_multiple_episodes(
            env, hypers['episodes per iteration'], hypers['steps per episode'],
            model, loss_fn, gym=args.openai_gym
        )
        all_final_rewards = discount_and_normalize_rewards(all_rewards,
                                                           hypers['discount'])

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

        if total_iter_reward > best_score:
            print('< < best score, keeping weights, backup model > >')
            best_weights = model.get_weights()
            best_score = total_iter_reward
            i_best = i
            model.save(f"_BAK_{best_score}_at_i{i_best}.h5")

        if total_iter_reward > total_steps*threshold_factor:
            smash_counter += 1

        print(f"done iter {i+1} of {hypers['iterations']} \
              - G_t={total_iter_reward} (G_best_ep: {best_ep_reward}) \
              <score: {best_score}> ({smash_counter})")

        if smash_counter > 5:
            break

    jsondumb = total_reward_progress

    if hypers['variance'] == 0:
        v_str = 'low'
    elif hypers['variance'] == 1:
        v_str = 'med'
    elif hypers['variance'] == 2:
        v_str = 'high'

    if args.openai_gym:
        inputs_str = '4'
        annshape_str = '5'
    else:
        if args.continue_ is None:
            inputs_str = args.inputs
            annshape_str = ''.join(args.shape)
        if args.continue_:
            inputs_str, annshape_str = hypers['info'][0], hypers['info'][1:]

    _disc = hypers["discount"]
    _steps = hypers["steps per episode"]
    _eps = hypers["episodes per interation"]
    modelname = f'pg_{v_str}_ref{int(args.reference)}_R{int(args.adv_reward)}' \
                + f'_{inputs_str}{annshape_str}_g{int(_disc*100)}' \
                + f'_s{_steps}_eps{_eps}_i{i_best+old_i}' \
                + f'_Gt{round(best_score)}'

    if args.openai_gym:
        modelname = f'pg_CartPole_{inputs_str}{annshape_str}_i{i_best+old_i}'

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
