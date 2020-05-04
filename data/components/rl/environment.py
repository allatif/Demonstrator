import math as m

import numpy as np

from ... import setup_sim, euler


class Environment:

    step_ = 0

    def __init__(self, euler_stepsize=0.001):
        self._euler_stepsize = euler_stepsize

        self._model = setup_sim.StateSpaceModel()

    def reset(self):
        Environment.step_ = 0
        rand_init_state = (np.random.rand(4) - 0.5) / 2.5
        # rand_init_state[0] = 0.
        # rand_init_state[1] = 0.
        # rand_init_state[2] = 0.
        # rand_init_state[3] = 0.3
        init_state_tuple = tuple(rand_init_state.tolist())
        self._sim = setup_sim.SimData(120_000, init_state_tuple)
        return rand_init_state

    def step(self, action):
        if action == 0:
            actionforce = -10000
        elif action == 1:
            actionforce = 10000
        done = False
        reward = 1.0
        _obs_ = euler.euler_method(self._model.A, self._model.B,
                                   self._sim.state_vec, self._sim.t_vec,
                                   self._euler_stepsize,
                                   self._sim.sim_length,
                                   Environment.step_,
                                   force=actionforce,
                                   steps_per_frame=30)
        _, x1, x2, x3, x4 = _obs_

        if abs(x3) > m.radians(30) or abs(x1) > 2.5:
            done = True
            reward = 0.

        Environment.step_ += 30

        return np.array([np.float(x1),
                         np.float(x2),
                         np.float(x3),
                         np.float(x4)]), reward, done
