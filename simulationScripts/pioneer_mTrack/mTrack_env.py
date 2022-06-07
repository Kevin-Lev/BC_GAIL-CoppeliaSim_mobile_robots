from math import sqrt
from imitation.data import rollout, types
import gym
import numpy as np
import sys
from gym import spaces, logger
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')


from simulationScripts.file import readDataImitation


class MTrack(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, filedir):
        super(MTrack, self).__init__()

        observations, actions, tipo = readDataImitation(filedir)
        observations = np.array(observations, dtype=np.float32)
        actions = np.array(actions, dtype=np.float32)

        trajectory = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

        transitions = rollout.flatten_trajectories([trajectory])

        self.obs = transitions.obs
        self.acts = transitions.acts
        self.next_obs = transitions.next_obs
        self.dones = transitions.dones

        obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
        obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
        act_lows = np.array([0.0, 0.0], dtype=np.float32) 
        act_highs = np.array([2.0, 2.0], dtype=np.float32) 

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
     
        self.accumate_reward += reward
        self.current_state_done = self.dones[self.transition_iteration]

        if self.current_state_done == False:
            self.transition_iteration += 1
            self.current_state = self.obs[self.transition_iteration]
            self.current_state_expected_action = self.acts[self.transition_iteration]
            self.next_state = self.next_obs[self.transition_iteration]

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