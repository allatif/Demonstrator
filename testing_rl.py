# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from time import sleep

import tensorflow as tf
from tensorflow import keras

from data.components.rl import environment as env


n_inputs = 4
model = keras.models.Sequential([
    keras.layers.Dense(5, activation="elu", input_shape=[n_inputs]),
    keras.layers.Dense(1, activation="sigmoid"),
])

"""
env = env.Environment()

obs = env.reset()
print(obs)

for s in range(200):
    action = 1
    obs, reward, done = env.step(action)
    # print(obs)
    # print("reward:", reward)
    # print(done)
    sleep(0.02)
    if done:
        print(s)
        break
"""
