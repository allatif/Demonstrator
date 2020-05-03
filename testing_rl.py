from time import sleep

from data.components.rl import environment as env


env = env.Environment()

obs = env.reset()
print(obs)

for s in range(200):
    obs, reward, done = env.step()
    # print(obs)
    # print("reward:", reward)
    # print(done)
    sleep(0.02)
    if done:
        print(s)
        break
