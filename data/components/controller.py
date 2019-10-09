import numpy as np


class StateSpaceController:

    def __init__(self, k1, k2, k3, k4):
        self.ss_K = np.matrix([k1, k2, k3, k4])
