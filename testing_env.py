from data.components.rl import environment as env


env = env.Environment(adv_reward=True, ref=True)
obs = env.reset()
print(obs)

action = 1

for step in range(100):
    obs, r, done = env.step(action)
    print(step+1, obs, r)
    if done:
        print('-> Failed at step', step+1)
        break
