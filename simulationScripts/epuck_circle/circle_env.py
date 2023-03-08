from math import sqrt
from imitation.data import rollout, types
import gym
import numpy as np
import sys
from gym import spaces, logger
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')


from simulationScripts.file import readDataImitation, readEpuckDataImitation


class CircleTrack(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, filedir):
        super(CircleTrack, self).__init__()

        # observations, actions, tipo = readDataImitation('simulationData/epuckCircle/withOrientation/training/10_4_2022/epuck_circle_0.txt')
        observations, actions, tipo = readEpuckDataImitation(filedir)
        # observations, actions, tipo = readEpuckDataImitation('simulationData/epuckCircletrack/withSensor/training/19_4_2022_definitivo/epuck_circle_0.txt')
        observations = np.array(observations, dtype=np.float32)
        actions = np.array(actions, dtype=np.float32)

        trajectory = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

        transitions = rollout.flatten_trajectories([trajectory])

        self.obs = transitions.obs
        self.acts = transitions.acts
        self.next_obs = transitions.next_obs
        self.dones = transitions.dones

        highest_left = 4.0
        highest_right = 4.0
        lowest_left = -1.0
        lowest_right = -1.0
        for act in actions:
           if act[0] > highest_left:
                highest_left = act[0]
           if act[1] > highest_right:
                highest_right = act[1]
           if act[0] < lowest_left:
                lowest_left = act[0]
           if act[1] < lowest_right:
                lowest_right = act[1]


        obs_lows = np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00], dtype=np.float32)
        obs_highs = np.array([0.10, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], dtype=np.float32)
        act_lows = np.array([lowest_left, lowest_right], dtype=np.float32) 
        act_highs = np.array([highest_left, highest_right], dtype=np.float32) 
        # act_lows = np.array([0.0, 0.0], dtype=np.float32) 
        # act_highs = np.array([3.40, 3.40], dtype=np.float32) 

        self.observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

        self.action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

        self.current_state = self.obs[0]
        self.current_state_expected_action = self.acts[0]
        self.current_state_done = self.dones[0]
        self.next_state = self.next_obs[0]
        self.transition_iteration = 0
        self.total_reward = 0.0
        self.accumate_reward = 0.0

    def step(self, action):
        # pass
        reward = 0.0
        # reward = 100
        # sqe = CircleTrack.squared_error(self.current_state_expected_action, action)
        # if sqe == 0.0:
        #     reward *= 5
        # else:
        #     reward /= 2
        # reward -= sqe
        self.accumate_reward += reward

        # self.current_state_done = self.dones[self.transition_iteration]
        # print('self.current_state')
        # print(self.current_state[0], self.current_state[1], self.current_state[2])

        # print('STATE')
        # print(self.current_state)
        # print('ACTION')
        # print(self.current_state_expected_action)
        # print('NEXT STATE')
        # print(self.next_state)
        # print('DONE')
        # print(self.current_state_done)

        self.current_state_done = self.dones[self.transition_iteration]

        if self.current_state_done == False:
            self.transition_iteration += 1
            self.current_state = self.obs[self.transition_iteration]
            self.current_state_expected_action = self.acts[self.transition_iteration]
            self.next_state = self.next_obs[self.transition_iteration]

            # if self.current_state_done == True:
            #     self.current_state_done = self.dones[self.transition_iteration]

            # print('PRÓXIMO STATE')
            # print(self.current_state)
            # print('PRÓXIMA ACTION')
            # print(self.current_state_expected_action)
            # print('PRÓXIMO NEXT STATE')
            # print(self.next_state)
            # print('DONE')
            # print(self.current_state_done)
        # else:
            # print('self.current_state FINAL')
            # print(self.current_state[0], self.current_state[1], self.current_state[2])
            # print('self.current_state_expected_action, action')
            # print(self.current_state_expected_action, action)
            # print('self.accumate_reward')
            # print(self.accumate_reward)
            # print('self.total_reward')
            # print(self.total_reward)
            # print('reward')
            # print(reward)
            # print('self.transition_iteration')
            # print(self.transition_iteration)

            # if self.accumate_reward > self.total_reward:
            #     print('antiga REWARD TOTAL')
            #     print(self.total_reward)
            #     print('NOVA REWARD TOTAL')
            #     print(self.accumate_reward)
            #     self.total_reward = self.accumate_reward


        return self.current_state, reward, self.current_state_done, {}
        
               

    def reset(self):
        # # return observation  # reward, done, info can't be included
        # print('RESET FOI CHAMADO')
        self.current_state = self.obs[0]
        self.current_state_expected_action = self.acts[0]
        self.next_state = self.next_obs[0]
        self.current_state_done = self.dones[0]
        self.transition_iteration = 0
        self.accumate_reward = 0.0
        # return self.state
        # pass
        return self.current_state
        
    def render(self, mode='human'):
        pass

    def close (self):
        pass

    def squared_error(expected_action, predicted_action):
        sq_error = pow((expected_action[0] - predicted_action[0]), 2) + pow((expected_action[1] - predicted_action[1]), 2)
        return sq_error