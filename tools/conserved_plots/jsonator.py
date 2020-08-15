import json


# Load modelname and rewards from json
modelname = 'pg_R751e2_58x6_spf50_g99_ag10k_s200_eps10_i1000'
jsonpath = '' + modelname + '.json'
total_reward_progress = json.load(open(jsonpath, 'r'))

sorted_rewards = total_reward_progress
sorted_rewards.sort(reverse=True)
print(sorted_rewards[:10])
