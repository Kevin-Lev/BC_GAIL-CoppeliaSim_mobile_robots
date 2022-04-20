
import numpy as np
import sys
import stable_baselines3 as sb3
from imitation.algorithms.adversarial import gail
from imitation.util import logger
from imitation.rewards import reward_nets
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from imitation.data import rollout, types
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from gym import spaces
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import readDataImitation
from longTrack_env import LongTrack


def testCall(rou):
    print('rou')
    print(rou)

timesteps = int(sys.argv[1])

observations, actions, tipo = readDataImitation('simulationData/pioneerLongTrack/withOrientation/training/24_3_2022_definitivo/pioneer_longTrack_0.txt')
batch_length = len(observations) - 1
observations = np.array(observations, dtype=np.float32)
actions = np.array(actions, dtype=np.float32)

print(observations)
print(actions)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

logdir = '/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/logs/'

# print('tes')
# print(tes)

transitions = rollout.flatten_trajectories([tes])

print('transitions')
print(transitions)

obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
# obs_highs = np.array(highs_array, dtype=np.float32)
obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
act_lows = np.array([0.0, 0.0], dtype=np.float32) 
act_highs = np.array([2.0, 2.0], dtype=np.float32) 

long_env = LongTrack()
vec_long_env = make_vec_env(lambda: long_env, n_envs=1)
# vec_long_env = DummyVecEnv([lambda: long_env] * 8)

# observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

# action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

print('vec_long_env.observation_space')
print(vec_long_env.observation_space)
print('vec_long_env.action_space')
print(vec_long_env.action_space)


gail_reward_net = reward_nets.BasicRewardNet(
    observation_space=vec_long_env.observation_space,
    action_space=vec_long_env.action_space
)

# print('gail_reward_net')
# print(gail_reward_net)

gail_logger = gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/logs/', ["stdout", "csv", "log", "tensorboard"])

learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=64, n_steps=64, ent_coef=0.001, n_epochs=30, vf_coef=0.5)
# learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
# learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


bc_policy = gail.GAIL(
    venv=vec_long_env,
    demonstrations=transitions,
    demo_batch_size=6,
    gen_algo=learner,
    # gen_algo=sb3.PPO("MlpPolicy", venv, verbose=1, n_steps=1024),
    reward_net=gail_reward_net,
    custom_logger=gail_logger
)


# learner_rewards_before_training, _ = evaluate_policy(
#     learner, vec_long_env, 1, return_episode_rewards=True
# )

# bc_policy.allow_variable_horizon = True

bc_policy.train(total_timesteps=timesteps, callback=testCall)

# learner_rewards_after_training, _ = evaluate_policy(
#     learner, vec_long_env, 1, return_episode_rewards=True
# )

# print('learner_rewards_before_training')
# print(learner_rewards_before_training)
# print('learner_rewards_after_training')
# print(learner_rewards_after_training)

bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')
# bc_policy.policy.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')

# bc_policy.policy.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')

bc_policy = bc_policy.policy


poseList = [[5.755764961242676, -3.500044584274292, 3.1415629386901855], [-3.045706033706665,-3.4710705280303955, 3.1387693881988525], [-3.6208038330078125,-3.037193536758423, 1.5786396265029907], [-3.371680498123169,3.044665813446045,1.5291599035263062], [-2.9313392639160156, 3.5916759967803955, -0.021358318626880646], [5.020373344421387,3.2646336555480957,-0.042220111936330795]]

print('Poses')
for pose in poseList:
    pred = bc_policy.predict(pose)
    print(pose)
    print(pred)

print('Poses 2')
for pose in poseList:
    pred = bc_policy.predict(pose)
    print(pose)
    print(pred)


# bc_policy.load()

# del bc_policy
print('Carregou GAIL!')

ppo_gail_trained = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')

print('Poses PPO GAIL TRAINED')
for pose in poseList:
    pred = ppo_gail_trained.predict(pose)
    print(pose)
    print(pred)