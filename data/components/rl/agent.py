import os

import numpy as np
import tensorflow as tf
from tensorflow import keras


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class Agent:

    def __init__(self):
        pass

    def load_model(self, name):
        path = 'data\\components\\rl\\models\\' + name
        self.model = keras.models.load_model(path)

    def act(self, obs):
        left_proba = self.model.predict(obs.reshape(1, -1))
        action = int(np.random.rand() > left_proba)
        if action == 0:
            return -10000
        elif action == 1:
            return 10000
