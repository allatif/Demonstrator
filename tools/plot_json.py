import json

import matplotlib.pyplot as plt
from data.components import colors


# Load Modelname, Loss and Rewards from json
f = open()
modelname = ''
loss_progress = []
total_reward_progress = []

# Plot Loss and Rewards
plt.figure(figsize=(12, 8), dpi=80, facecolor=(colors.get_pp(colors.WHITE)))

plt.subplot(211)
plt.plot(loss_progress, color=colors.get_pp(colors.LBLUE))
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.grid(True)

plt.subplot(212)
plt.plot(total_reward_progress, color=colors.get_pp(colors.TOMATO))
plt.xlabel('Iterations')
plt.ylabel('Total Rewards')
plt.grid(True)

plt.savefig(f"{modelname}.png")
