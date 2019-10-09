import numpy as np

from data.components import inertia

GRAVITY = 9.81


class Demonstrator(object):

    def __init__(self, mass_sphere, mass_cart, radius, thickness_sphere):
        self._m_sphere = mass_sphere  # [Kg]
        self._m_cart = mass_cart  # [Kg]
        self._radius = radius  # [m]
        self._radius_i = radius - thickness_sphere  # [m]
        self._inertia = inertia.Inertia(mass_sphere, 'hollow_sphere',
                                        self._radius, self._radius_i)

        # inertia by sphere:
        self._J = self._inertia.value

        # common divisor by matrix elements
        self.comdiv = (
            (self._J + self._m_sphere*self._radius**2)
            * (self._m_cart + self._m_sphere)
            - (self._m_sphere**2 * self._radius**2)
        )

    def engineinit(self, K_torque, K_gear, resistor, radius):
        # engine parameters for statespace:
        self.K_M_1 = (K_torque*K_gear) / (resistor*radius)
        self.K_M_2 = (K_torque**2 * K_gear**2) / (resistor*radius)

    def statespace(self):
        a23, a43 = self._calc_a23(), self._calc_a43()
        b2, b4 = self._calc_b2(), self._calc_b4()
        self.ss_A = np.matrix([
            [0, 1, 0, 0],
            [0, -b2*self.K_M_2, a23, 0],
            [0, 0, 0, 1],
            [0, -b4*self.K_M_2, a43, 0]
        ])
        self.ss_B = np.matrix([0, b2*self.K_M_1, 0, b4*self.K_M_1]).T
        self.ss_C = np.matrix([1, 0, 0, 0])
        self.ss_D = np.matrix([0])

    @property
    def radius(self):
        return self._radius

    @property
    def inner_radius(self):
        return self._radius_i

    @property
    def mass_sphere(self):
        return self._m_sphere

    @property
    def J(self):
        return self._J

    # Calculation of matrix elements a23, a43, b2 and b4:
    def _calc_a23(self):
        return -(self._m_sphere**2 * self._radius**2 * GRAVITY) \
            / self.comdiv

    def _calc_a43(self):
        return (self._m_sphere * self._radius * GRAVITY
                * (self._m_cart+self._m_sphere)) \
            / self.comdiv

    def _calc_b2(self):
        return (self._J + self._m_sphere*self._radius**2) \
            / self.comdiv

    def _calc_b4(self):
        return -(self._m_sphere * self._radius) \
            / self.comdiv


###############################################################################


class Prefilter:

    def __init__(self, ss_A, ss_B, ss_C, ss_K):
        self.ss_A = ss_A
        self.ss_B = ss_B
        self.ss_C = ss_C
        self.ss_K = ss_K

    def calc_P_prefilter(self):
        P = -(
            (self.ss_C * (self.ss_A + self.ss_B*self.ss_K).I) * self.ss_B
        ).I
        return P[0, 0]
