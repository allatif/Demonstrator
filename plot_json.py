import json

import matplotlib.pyplot as plt
from data.components import colors


# Load modelname and rewards from json
modelname = 'deepq3216_b64_s200_ep1000(100)_sc200'
jsonpath = 'tools\\conserved_plots\\' + modelname + '.json'
total_reward_progress = json.load(open(jsonpath, 'r'))

# Plot Loss and Rewards
plt.figure(figsize=(12, 8), dpi=80, facecolor=(colors.get_pp(colors.WHITE)))
plt.plot(total_reward_progress, color=colors.get_pp(colors.TOMATO))
plt.xlabel('Episode')  # Iteration
plt.ylabel('Total rewards')
plt.grid(True)

plt.savefig(f"{modelname}.png")
