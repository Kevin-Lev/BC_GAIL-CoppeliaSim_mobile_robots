from math import sqrt
from imitation.data import rollout, types
import gym
import numpy as np
import sys
from gym import spaces, logger
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')


from simulationScripts.file import readDataImitation, readEpuckDataImitation


class ZTrackGeneralized(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, filedir1, filedir2, filedir3):
        super(ZTrackGeneralized, self).__init__()

        observations1, actions1, _ = readEpuckDataImitation(filedir1)
        observations2, actions2, _ = readEpuckDataImitation(filedir2)
        observations3, actions3, _ = readEpuckDataImitation(filedir3)
        
        observations1 = np.array(observations1, dtype=np.float32)
        actions1 = np.array(actions1, dtype=np.float32)
        observations2 = np.array(observations2, dtype=np.float32)
        actions2 = np.array(actions2, dtype=np.float32)
        observations3 = np.array(observations3, dtype=np.float32)
        actions3 = np.array(actions3, dtype=np.float32)

        trajectory = types.Trajectory(obs=observations1, acts=actions1, infos=None, terminal=True)
        trajectory2 = types.Trajectory(obs=observations2, acts=actions2, infos=None, terminal=True)
        trajectory3 = types.Trajectory(obs=observations3, acts=actions3, infos=None, terminal=True)

        transitions = rollout.flatten_trajectories([trajectory, trajectory2, trajectory3])

        self.obs = transitions.obs
        self.acts = transitions.acts
        self.next_obs = transitions.next_obs
        self.dones = transitions.dones

        obs_lows = np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00], dtype=np.float32)
        obs_highs = np.array([0.10, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], dtype=np.float32)
        act_lows = np.array([0.0, 0.0], dtype=np.float32) 
        act_highs = np.array([4.5, 4.5], dtype=np.float32) 

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
        self.current_state = self.obs[0]
        self.current_state_expected_action = self.acts[0]
        self.next_state = self.next_obs[0]
        self.current_state_done = self.dones[0]
        self.transition_iteration = 0
        self.accumate_reward = 0.0

        return self.current_state
        
    def render(self, mode='human'):
        pass

    def close (self):
        pass

    def squared_error(expected_action, predicted_action):
        sq_error = pow((expected_action[0] - predicted_action[0]), 2) + pow((expected_action[1] - predicted_action[1]), 2)
        return sq_error