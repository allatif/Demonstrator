import numpy as np
import matplotlib.pyplot as plt


sim_length = 8000
dt = 0.001

y = np.zeros((sim_length+1, 1))
u1 = np.zeros((sim_length+1, 1))
u2 = np.zeros((sim_length+1, 1))
t_vec = np.zeros((sim_length+1, 1))

# Initial Conditions
u1[0] = 0.1
u2[0] = -2


class SystemPT2:

    def __init__(self, mass, spring, damper):
        self.m = mass  # [Kg]
        self.c = spring  # spring rate [N/m]
        self.D = damper  # damping rate [N*sec/m]

    def spacestate(self):
        self.A = np.array([
            (0, 1),
            (-(self.c/self.m), -(self.D/self.m))
        ])
        self.B = np.array([0, 0])
        self.C = np.array([1, 0])
        self.D = np.array([0])

    def disturbance(self, force):
        self.B = np.array([0, force])


FMD = SystemPT2(5, 85, 20)
FMD.spacestate()

# EULER
for k in range(sim_length):
    u1[k+1] = u1[k] + dt*(u1[k]*FMD.A[0, 0] + u2[k]*FMD.A[0, 1])
    u2[k+1] = u2[k] + dt*(u1[k]*FMD.A[1, 0] + u2[k]*FMD.A[1, 1])

    y[k] = u1[k]*FMD.C[0] + u2[k]*FMD.C[1]
    t_vec[k+1] = t_vec[k] + dt

plt.plot(t_vec, y)
plt.grid(True)
plt.show()
