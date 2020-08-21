import os

import numpy as np

print(" -- Loading TensorFlow -- ")
from tensorflow import keras


# Just disables the warning, doesn't enable AVX/FMA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class Agent:

    def __init__(self, sensibility=10000):
        self._sens = sensibility

        self._force = 0
        self._running = True
        self._type = None
        self._input_size = None

    def load_model(self, model_name):
        path = 'data\\components\\rl\\models\\' + model_name
        self.model = keras.models.load_model(path, compile=False)
        self._input_size = self.model.input.shape[1]
        outputsize = self.model.output.shape[1]
        if outputsize == 1:
            self._type = 'REINFORCE'
        elif outputsize == 2:
            self._type = 'DQL'
        print(f"Finished loading {self._type} model")

    def act(self, obs):
        left_proba = self.model.predict(obs.reshape(1, -1))
        action = int(np.random.rand() > left_proba)
        if action == 0:
            return -self._sens
        elif action == 1:
            return self._sens

    def qact(self, obs):
        Q_values = self.model.predict(obs.T)
        action = np.argmax(Q_values[0])
        if action == 0:
            return -self._sens
        elif action == 1:
            return self._sens

    def observe(self, obs):
        self._obs = obs
        if self._input_size < obs.size:
            self._obs = np.delete(obs, self._input_size, 0)

    def update(self):
        if self._type == 'DQL':
            if self._running:
                self._force = self.qact(self._obs)
            elif not self._running:
                self._force = 0
        elif self._type == 'REINFORCE':
            if self._running:
                self._force = self.act(self._obs)
            elif not self._running:
                self._force = 0

    def stop(self):
        self._running = False

    def _trainact(self, action):
        if action == 0:
            self._force = -self._sens
        elif action == 1:
            self._force = self._sens

    @property
    def force(self):
        return self._force

    @property
    def obs(self):
        return self._obs
