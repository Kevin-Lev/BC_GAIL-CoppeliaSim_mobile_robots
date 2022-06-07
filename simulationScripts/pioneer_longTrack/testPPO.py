import numpy as np
import sys
import stable_baselines3 as sb3
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from imitation.data import rollout, types
from stable_baselines3.common.policies import get_policy_from_name
from stable_baselines3.common.policies import ActorCriticPolicy
from gym import spaces
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import readDataImitation
from longTrack_env import LongTrack

def go():
    print('hey')

total_timesteps = int(sys.argv[1])

observations, actions, tipo = readDataImitation('simulationData/pioneerLongTrack/withOrientation/training/24_3_2022_definitivo/pioneer_longTrack_0.txt')
filedir = 'simulationData/pioneerLongTrack/withOrientation/training/24_3_2022_definitivo/pioneer_longTrack_0.txt'
batch_length = len(observations) - 1
observations = np.array(observations, dtype=np.float32)
actions = np.array(actions, dtype=np.float32)

print(observations)
print(actions)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

# print('tes')
# print(tes)

transitions = rollout.flatten_trajectories([tes])

print('transitions')
print(transitions)



print('transitions with rewards')
print(transitions)

obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
# obs_highs = np.array(highs_array, dtype=np.float32)
obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
act_lows = np.array([0.0, 0.0], dtype=np.float32) 
act_highs = np.array([2.0, 2.0], dtype=np.float32) 

long_env = LongTrack(filedir)
vec_long_env = make_vec_env(lambda: long_env, n_envs=1, monitor_dir='simulationScripts/pioneer_longTrack/')

logdir = '/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/logs/'

ppo = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=3, n_steps=3, ent_coef=0.01, n_epochs=3, vf_coef=0.2, tensorboard_log=logdir)
# ppo = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=6, n_steps=6)

# mlp = get_policy_from_name(base_policy_type=ActorCriticPolicy,name="MlpsdPolicy")

# print('mlp')
# print(mlp)

# ppo.collect_rollouts(vec_long_env, go(), rollout_buffer=transitions, n_rollout_steps=1)

ppo.learn(total_timesteps, tb_log_name="PPO_tradicional")
ppo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/ppo_attributes_and_params.zip')
ppo.policy.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/ppo_policy.zip')

# ppo.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/ppo_attributes_and_params.zip')
# ppo.policy.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/ppo_policy.zip')

poseList = [[5.755764961242676, -3.500044584274292, 3.1415629386901855], [-3.045706033706665,-3.4710705280303955, 3.1387693881988525], [-3.6208038330078125,-3.037193536758423, 1.5786396265029907], [-3.371680498123169,3.044665813446045,1.5291599035263062], [-2.9313392639160156, 3.5916759967803955, -0.021358318626880646], [5.020373344421387,3.2646336555480957,-0.042220111936330795]]

print('Poses')
for pose in poseList:
    pose = np.array(pose, dtype=np.float32) 
    pred = ppo.policy.predict(pose)
    print(pose)
    print(pred)

print('Poses 2')
for pose in poseList:
    pose = np.array(pose, dtype=np.float32) 
    pred = ppo.policy.predict(pose)
    print(pose)
    print(pred)

del ppo

ppo = PPO.load(path='/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/PPO/pioneerLongtrackwithOrientation/ppo_attributes_and_params.zip', env=vec_long_env)


print('Poses LOAD')
for pose in poseList:
    pose = np.array(pose, dtype=np.float32) 
    pred = ppo.policy.predict(pose)
    print(pose)
    print(pred)

# action = ppo.predict([5.755764961242676, -3.500044584274292, 3.1415629386901855])
# print('action')
# print(action)
