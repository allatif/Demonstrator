import numpy as np
import control
import matplotlib.pyplot as plt

from data import setup_sim

sim = setup_sim.SimData(12000)

A = sim.system
B = np.matrix([0, 1, 0, 1]).T
C = np.matrix([1, 0, 0, 0])
D = np.matrix([0])

ss_sys = control.ss(A, B, C, D)

print(ss_sys)

# control.root_locus(ss_sys)

# plt.plot([1, 2, 3, 4])
# plt.show()

num = np.array([2, 5, 1])
den = np.array([1, 2, 3])

h = control.tf(num, den)

print(h)

control.root_locus(h, grid=True)
plt.show()
