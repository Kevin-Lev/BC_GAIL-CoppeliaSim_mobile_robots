from imitation.algorithms import bc
from imitation.data import rollout
from imitation.util import logger, util
# import gym
import pickle

# with open("tests/testdata/expert_models/cartpole_0/rollouts/final.pkl", "rb") as f:
#     # This is a list of `imitation.data.types.Trajectory`, where
#     # every instance contains observations and actions for a single expert
#     # demonstration.
#     trajectories = pickle.load(f)

# print('trajectories')
# print(trajectories)

# env = gym.make('CartPole-v0')

venv = util.make_vec_env("CartPole-v0", n_envs=2)
print('observation_space')
print(venv.observation_space)
print('action space')
print(venv.action_space)