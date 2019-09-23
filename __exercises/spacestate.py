import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

A = -8.0
B = 2.0
C = 1.0
D = 0.0
sys1 = signal.StateSpace(A, B, C, D)
t1, y1 = signal.step(sys1)

plt.plot(t1, y1)
plt.grid(True)
plt.show()
