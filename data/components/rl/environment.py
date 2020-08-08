import math as m

import numpy as np

from . import agent
from ... import setup_sim, euler


class Environment:

    step_ = 0

    def __init__(self, euler_stepsize=0.001, adv_reward=False):
        self._euler_stepsize = euler_stepsize

        self._adv_reward = adv_reward
        self._model = setup_sim.StateSpaceModel()
        self._agent = agent.Agent(sensibility=20000)

    def reset(self):
        Environment.step_ = 0

        rand_init_x1 = np.random.uniform(low=-1.0, high=1.0, size=1)
        rand_init_x2 = np.random.uniform(low=-2.0, high=2.0, size=1)
        rand_init_x3 = np.random.uniform(low=-0.2, high=0.2, size=1)
        rand_init_x4 = np.random.uniform(low=-0.5, high=0.5, size=1)
        rand_init_state = np.concatenate(
            (rand_init_x1, rand_init_x2, rand_init_x3, rand_init_x4), axis=0
        )

        init_state_tuple = tuple(rand_init_state.tolist())
        self._sim = setup_sim.SimData(120_000, init_state_tuple)
        return rand_init_state

    def step(self, action):
        self._agent._trainact(action)

        done = False
        reward = 0

        spf = 30
        fakefps = 1 / (self._euler_stepsize*spf)
        _obs_ = euler.euler_method(self._model.A, self._model.B,
                                   self._sim.state_vec, self._sim.t_vec,
                                   fakefps, spf, Environment.step_,
                                   control_object=self._agent)
        x1, x2, x3, x4, _ = _obs_

        if abs(x3) > m.radians(20) or abs(x1) > 1.5:
            done = True

        if self._adv_reward:
            reward = self.rewarder(x1, x3)
        else:
            reward = 1
            if done:
                reward = 0

        Environment.step_ += spf

        return np.array([np.float(x1),
                         np.float(x2),
                         np.float(x3),
                         np.float(x4)]), reward, done

    def rewarder(self, location, angle, ratio=0.5):
        reward = ratio*self._loc_rewardf(location, m=2) \
            + (1-ratio)*self._ang_rewardf(angle)
        return reward

    @staticmethod
    def _ang_rewardf(ang, sigma=0.07, b=None, multi=0.25):
        if b is None:
            r_max = Environment._ang_rewardf(0, sigma, b=0, multi=multi)
            b = 1 - r_max
        return ((m.exp(-(ang/sigma)**2/2)) / (sigma*m.sqrt(2*m.pi)))*multi + b

    @staticmethod
    def _loc_rewardf(loc, m=1):
        return 1 - m*abs(loc)
