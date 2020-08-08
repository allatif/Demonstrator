import json

import matplotlib.pyplot as plt
from data.components import colors


# Load modelname and rewards from json
modelname = 'deepq_s200_ep600'
jsonpath = 'tools\\conserved_plots\\' + modelname + '.json'
total_reward_progress = json.load(open(jsonpath, 'r'))

# Plot Loss and Rewards
plt.figure(figsize=(12, 8), dpi=80, facecolor=(colors.get_pp(colors.WHITE)))
plt.plot(total_reward_progress, color=colors.get_pp(colors.TOMATO))
plt.xlabel('Episoden')
plt.ylabel('Gesamt-Rewards')
plt.grid(True)

plt.savefig(f"{modelname}.png")
