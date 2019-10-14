import numpy as np

from data.components import demonstrator as demo
from data.components import controller as cnt


class SimData:

    def __init__(self, sim_length, initial_state=(0, 0, 0, 0.3)):
        self.sim_length = sim_length

        x1 = np.zeros((self.sim_length+1, 1))
        x2 = np.zeros((self.sim_length+1, 1))
        x3 = np.zeros((self.sim_length+1, 1))
        x4 = np.zeros((self.sim_length+1, 1))

        # Initial Conditions
        x1[0] = initial_state[0]  # x -- traveled distance
        x2[0] = initial_state[1]  # x' -- velocity
        x3[0] = initial_state[2]  # ω -- angle
        x4[0] = initial_state[3]  # ω' -- angular veloctiy

        self.state_vec = x1, x2, x3, x4
        self.t_vec = np.zeros((self.sim_length+1, 1))

        # Initialize Kegel-Kugel-Demonstrator as k_k
        self.k_k = demo.Demonstrator(
            mass_sphere=19.5,
            mass_cart=84.2,
            radius=0.5,
            thickness_sphere=0.004
        )
        self.k_k.engineinit(
            K_torque=0.0253,
            K_gear=0.005,
            resistor=0.228,
            radius=0.006
        )
        self.k_k.statespace()

        default_Kregs = -1296.6, -3161.2, -31800, -9831
        self.controller = cnt.StateSpaceController(*default_Kregs)

    def update(self):
        self.system = (self.k_k.ss_A - self.k_k.ss_B*self.controller.ss_K)

    def set_Kregs(self, k1, k2, k3, k4):
        self.controller = cnt.StateSpaceController(k1, k2, k3, k4)

    def get_poles(self):
        return np.linalg.eig(self.system)[0]

    @property
    def A(self):
        return self.k_k.ss_A

    @property
    def B(self):
        return self.k_k.ss_B

    @property
    def K(self):
        return self.controller.ss_K
