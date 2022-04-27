import sys
import numpy as np
from gym import spaces
from imitation.data import rollout, types
from imitation.util import logger
from imitation.algorithms import bc
from imitation.algorithms.adversarial import gail
from stable_baselines3.common.env_util import make_vec_env
from imitation.rewards import reward_nets
import stable_baselines3 as sb3
from longTrack_env import LongTrack

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readDataImitation

total_epochs = int(sys.argv[1])
filedir = sys.argv[2]
imitation_method = sys.argv[3]

observations, actions, tipo = readDataImitation(filedir)

print('TIPO')
print(tipo)
# observations.append([5.024043083190918, 3.3925983905792236, -0.013310858979821205])
# observations.append([5.016650676727295, 3.2497057914733887, -0.042145781219005585])

batch_length = len(observations) - 1
observations = np.array(observations, dtype=np.float32)
actions = np.array(actions, dtype=np.float32)

print(observations)
print(actions)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

print('tes')
print(tes)

transitions = rollout.flatten_trajectories([tes])

print('transitions')
print(len(transitions))
print(transitions)
# print(transitions[1])
# print(transitions[1])
# print(transitions[21])

# Pos x:  max: +7.2055   min: -7.1195
# Pos y:  max: +4.7250   min: -4.7250
# ori     max: +3.141592 min: -3.141592
#wheel_speed max: 2.0    min: 0.0

# lows_array = []
# highs_array = []
# lows_array.append(-7.1195e+00)
# lows_array.append(-4.7250e+00)
# highs_array.append(7.1195e+00)
# highs_array.append(4.7250e+00)

# if tipo == 'withOrientation':
#     print('TIPO WITH ORIENTATION')
#     lows_array.append(-3.141592)
#     highs_array.append(3.141592)

# elif tipo == 'withSensor':
#     print('TIPO WITH SENSOR')
#     lows_array.append(-3.141592)
#     highs_array.append(3.141592)
    
#     for i in range(1086):
#         lows_array.append(-1)
#         highs_array.append(10.0)

# print('lows_array')
# print(lows_array)
# obs_lows = np.array(lows_array, dtype=np.float32)
obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
# obs_highs = np.array(highs_array, dtype=np.float32)
obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
act_lows = np.array([0.0, 0.0], dtype=np.float32) 
act_highs = np.array([2.0, 2.0], dtype=np.float32) 


observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

print('observation_space')
print(observation_space)
print('action_space')
print(action_space)

if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrack" + tipo + "/logs/")
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=observation_space,
        action_space=action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length     
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrack" + tipo + "/bc_policy.zip")

    # /home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrackwithOrientation

else:

    long_env = LongTrack()
    vec_long_env = make_vec_env(lambda: long_env, n_envs=1)
    # vec_long_env = DummyVecEnv([lambda: long_env] * 8)

    # observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

    # action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

    print('vec_long_env.observation_space')
    print(vec_long_env.observation_space)
    print('vec_long_env.action_space')
    print(vec_long_env.observation_space)


    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_long_env.observation_space,
        action_space=vec_long_env.action_space
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=1, tensorboard_log=logdir, target_kl=0.003)
    # learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
    # learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


    bc_policy = gail.GAIL(
        venv=vec_long_env,
        demonstrations=transitions,
        demo_batch_size=6,
        gen_algo=learner,
        # gen_algo=sb3.PPO("MlpPolicy", venv, verbose=1, n_steps=1024),
        reward_net=gail_reward_net
        custom_logger=gail_logger
    )


    # learner_rewards_before_training, _ = evaluate_policy(
    #     learner, vec_long_env, 1, return_episode_rewards=True
    # )

    # bc_policy.allow_variable_horizon = True

    bc_policy.train(total_timesteps=total_epochs)


    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')





