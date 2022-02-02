import numpy as np
import time
import os
import matplotlib.pyplot as plt
import pygame

a = np.load("env-11x11-20.npy")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
BLUE = (255, 0, 255)
YELLOW = (255, 255, 0)

AGENT = 1
TARGET = 2
HOLE = 99

WIDTH_MAX = 600
LEN = len(a)

VEL = WIDTH_MAX // LEN

SHAPE = VEL - 1
WIDTH = VEL * LEN + 1
HEIGHT = WIDTH


def clear():
    os.system("cls")


class GridWorld:

    def __init__(self, env, agent, target):
        self.env = env
        self.env_start = env
        self.agent = agent
        self.agent_start = agent
        self.target = target
        self.target_reward = 2
        self.out_reward = -2
        self.step_reward = -0.025
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.game_flip = True
        self.fps = 60
        self.best = False

    def play(self, q_table=None, itr=1, fps=60, flip=True):
        self.fps = fps
        self.game_flip = flip
        total_action = 0
        game_win = False
        for _ in range(itr):
            over = False
            state = self.reset()
            total_action = 0
            while not over:
                action = np.argmax(q_table[state[0]][state[1]])
                state, rew, over = self.move(action)
                total_action += 1
                if total_action > LEN * LEN:
                    over = True
            if rew == self.target_reward:
                game_win = True
            else:
                game_win = False
        return total_action, game_win

    def draw_game(self, q_table):
        for i in range(LEN+1):
            pygame.draw.line(self.win, WHITE, (i*VEL, 0), (i*VEL, LEN*VEL))
            pygame.draw.line(self.win, WHITE, (0, i*VEL), (LEN*VEL, i*VEL))
        for i in range(LEN):
            for j in range(LEN):
                if self.env[i][j] == HOLE:
                    pygame.draw.rect(self.win, RED,
                                     (VEL*j+1, VEL*i+1, SHAPE, SHAPE))
                else:
                    value = max(q_table[i][j])
                    if value > 0:
                        value *= 100
                        if value > 255:
                            value = 255
                        else:
                            pass
                        pygame.draw.rect(self.win, (0, 0, value),
                                         (VEL*j+1, VEL*i+1, SHAPE, SHAPE))
        pygame.draw.rect(self.win, GREEN,
                         (VEL*self.target[1]+1,
                          VEL*self.target[0]+1, SHAPE, SHAPE))
        pygame.draw.rect(self.win, YELLOW,
                         (VEL*self.agent[1]+1,
                          VEL*self.agent[0]+1, SHAPE, SHAPE))

    def get_path(self, q_table):
        path = np.zeros((LEN, LEN), dtype='<U11')
        for i in range(LEN):
            for j in range(LEN):
                action = np.argmax(q_table[i][j])
                if action == 0:
                    path[i][j] = "↑"
                elif action == 1:
                    path[i][j] = "↓"
                elif action == 2:
                    path[i][j] = "→"
                elif action == 3:
                    path[i][j] = "←"
        return path

    def reset(self):
        self.agent = self.agent_start.copy()
        return self.agent.copy()

    def move(self, action):
        self.win.fill(BLACK)
        self.draw_game(q_table)
        if self.game_flip:
            pygame.display.flip()
            clock.tick(self.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if not self.game_flip:
                    self.game_flip = True
                elif self.game_flip:
                    self.game_flip = False
            elif keys[pygame.K_r]:
                over = True
        over = False
        if action == 0:
            self.agent[0] -= 1
        elif action == 1:
            self.agent[0] += 1
        elif action == 2:
            self.agent[1] += 1
        elif action == 3:
            self.agent[1] -= 1
        """
        elif action == 4:
            self.agent[0] -= 1
            self.agent[1] += 1
        elif action == 5:
            self.agent[0] += 1
            self.agent[1] += 1
        elif action == 6:
            self.agent[0] += 1
            self.agent[1] -= 1
        elif action == 7:
            self.agent[0] -= 1
            self.agent[1] -= 1
        """
        if self.agent[0] < 0 or self.agent[0] > LEN - 1 \
                or self.agent[1] < 0 or self.agent[1] > LEN - 1:
            over = True
            reward = self.out_reward
        elif self.agent[0] == self.target[0] \
                and self.agent[1] == self.target[1]:
            over = True
            reward = self.target_reward
        elif self.env[self.agent[0]][self.agent[1]] == HOLE:
            over = True
            reward = self.out_reward
        else:
            reward = self.step_reward
        return self.agent.copy(), reward, over

# 0 = up
# 1 = down
# 2 = left
# 3 = right


def get_agent_target(env):
    agent = []
    target = []
    for i in range(LEN):
        for j in range(LEN):
            if env[i][j] == AGENT:
                agent = [i, j]
            elif env[i][j] == TARGET:
                target = [i, j]
            else:
                pass
    return agent.copy(), target.copy()


def get_env(env, agent, target):
    env[agent[0]][agent[1]] = 0
    env[target[0]][target[1]] = 0
    return env


pygame.init()
pygame.display.set_caption("Simple GridWorld")
clock = pygame.time.Clock()
ag, ta = get_agent_target(a)
envi = get_env(a, ag.copy(), ta.copy())
env = GridWorld(envi, ag.copy(), ta.copy())
q_table = np.zeros((LEN, LEN, 4))
np.save("q_table.npy", q_table)
# np.random.seed(1)
max_iter = 1000
epsilon = 0
starting_eps = epsilon
epsilon_min = 0
epsilon_decay_val = (epsilon-epsilon_min) / (max_iter*0.9)
# discount = 0.1
learning_rate = 0.7
episode_reward = 0
avg_move_count = 50
best_action = (LEN - 1) * 4
# goal = 11
converged = False
avg_move = []
act = 1
show = 10
best_action_counter = 0


ep_reward = []
avg_move = []
ep_eps = {'ep': [], 'eps': []}
ep_lr = {'ep': [], 'lr': []}
ep_dr = {'ep': [], 'dr': []}
y = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7',
     '0.8', '0.9', '0.99', '0.999', '1']
ep_y = {'ep': [], 'y': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                        0.7, 0.8, 0.9, 0.99, 0.999, 1]}
num_actins = {'ep': [], 'lr': [], 'eps': [], 'act': []}
data = {'ep': [], 'avg': [], 'min': [], 'max': [], 'eps': []}
for discount in ep_y['y']:
    pygame.display.set_caption(f"gamma={discount}")
    act = 1
    converged = False
    failed = False
    q_table = np.zeros((LEN, LEN, 4))
    best_action = (LEN - 1) * 4
    best_action_counter = 0
    while not converged:
        over = False
        episode_reward = 0
        state = env.reset()
        actions = 0
        while not over:
            if np.random.random() > epsilon:
                action = np.argmax(q_table[state[0]][state[1]])
            else:
                action = np.random.randint(0, 3)
            new_state, reward, over = env.move(action)
            actions += 1
            episode_reward += reward
            if not over:
                max_future_q_value = np.max(q_table[new_state[0]][new_state[1]])
                current_q_value = q_table[state[0]][state[1]][action]
                new_q_value = current_q_value+learning_rate *\
                    (reward+discount*max_future_q_value-current_q_value)
                q_table[state[0]][state[1]][action] = new_q_value
                if actions > LEN * LEN * 2:
                    over = True
                    converged = True
                    failed = True
                    print("failed")
            elif over:
                avg_move.append(actions)
                q_table[state[0]][state[1]][action] = reward
                if reward == env.target_reward:
                    if actions < best_action:
                        best_action_counter = 0
                        best_action = actions
                        print(f"{act} BEST episode with {best_action} lr={learning_rate} eps={epsilon}")
                        actions, win = env.play(q_table=q_table, fps=60, flip=False)
                        if win and actions <= best_action:
                            np.save(f"q_itr-{act}_gamma-{discount}_act-{actions}.npy", q_table)
                    elif actions == best_action:
                        print("best action repeating", best_action_counter)
                        best_action_counter += 1
                        if best_action_counter == 40:
                            converged = True
                            print("converged")
            state = new_state
        ep_reward.append(episode_reward)
        if act % show == 0:
            np.save("q_table.npy", q_table)
        act += 1
        if env.game_flip:
            print(act, "- discoun_rate:", discount)
    if failed:
        ep_y['ep'].append(0)
    elif not failed:
        ep_y['ep'].append(act - 40)

plt.bar(y, ep_y['ep'], width=0.2)
plt.show()
env.play(q_table=q_table, itr=1000, fps=20, flip=True)
pygame.quit()
