import os

import numpy as np

print(" -- Loading TensorFlow -- ")
from tensorflow import keras


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class Agent:

    def __init__(self, sensibility=10000):
        self._sens = sensibility

        self._force = 0.0

    def load_model(self, model_name):
        path = 'data\\components\\rl\\models\\' + model_name
        self.model = keras.models.load_model(path, compile=False)
        print("Finished loading model")

    def act(self, obs):
        left_proba = self.model.predict(obs.reshape(1, -1))
        action = int(np.random.rand() > left_proba)
        if action == 0:
            return -self._sens
        elif action == 1:
            return self._sens

    def observe(self, obs):
        self._obs = obs

    def update(self):
        self._force = self.act(self._obs)

    @property
    def force(self):
        return self._force

    @property
    def obs(self):
        return self._obs
