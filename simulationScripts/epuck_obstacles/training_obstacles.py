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
from stable_baselines3.common.policies import ActorCriticPolicy
import torch as th
from obstacles_env import ObstaclesTrack

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readEpuckDataImitation, readEpuckDataImitationOnlyDistance

total_epochs = int(sys.argv[1])
filedir = sys.argv[2]
imitation_method = sys.argv[3]
nets_number = int(sys.argv[4])

# observations, actions, tipo = readEpuckDataImitationOnlyDistance(filedir)
observations, actions, tipo = readEpuckDataImitation(filedir)
print('observations')
print(observations)
# observations2, actions2, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_1.txt_filtered.txt')
# observations3, actions3, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_2.txt_filtered.txt')
# observations4, actions4, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_3.txt_filtered.txt')
# observations5, actions5, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_4.txt_filtered.txt')
# observations6, actions6, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_5.txt_filtered.txt')
# observations7, actions7, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_6.txt_filtered.txt')
# observations8, actions8, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_7.txt_filtered.txt')
# observations9, actions9, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_8.txt_filtered.txt')
# observations10, actions10, tipo = readEpuckDataImitation('simulationData/epuckObstaclestrack/withSensor/training/10_11_2022/epuck_obstaclesTrack_9.txt_filtered.txt')

print('TIPO')
print(tipo)
print('Quantidade camada oculta:')
print(nets_number)

batch_length = len(observations) - 1
observations = np.array(observations, dtype=np.float32)
# observations2 = np.array(observations2, dtype=np.float32)
# observations3 = np.array(observations3, dtype=np.float32)
# observations4 = np.array(observations4, dtype=np.float32)
# observations5 = np.array(observations5, dtype=np.float32)
# observations6 = np.array(observations6, dtype=np.float32)
# observations7 = np.array(observations7, dtype=np.float32)
# observations8 = np.array(observations8, dtype=np.float32)
# observations9 = np.array(observations9, dtype=np.float32)
# observations10 = np.array(observations10, dtype=np.float32)

actions = np.array(actions, dtype=np.float32)
# actions2 = np.array(actions2, dtype=np.float32)
# actions3 = np.array(actions3, dtype=np.float32)
# actions4 = np.array(actions4, dtype=np.float32)
# actions5 = np.array(actions5, dtype=np.float32)
# actions6 = np.array(actions6, dtype=np.float32)
# actions7 = np.array(actions7, dtype=np.float32)
# actions8 = np.array(actions8, dtype=np.float32)
# actions9 = np.array(actions9, dtype=np.float32)
# actions10 = np.array(actions10, dtype=np.float32)

print('batch_length')
print(batch_length)
# print(observations)
# print(actions)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)
# tes2 = types.Trajectory(obs=observations2, acts=actions2, infos=None, terminal=True)
# tes3 = types.Trajectory(obs=observations3, acts=actions3, infos=None, terminal=True)
# tes4 = types.Trajectory(obs=observations4, acts=actions4, infos=None, terminal=True)
# tes5 = types.Trajectory(obs=observations5, acts=actions5, infos=None, terminal=True)
# tes6 = types.Trajectory(obs=observations6, acts=actions6, infos=None, terminal=True)
# tes7 = types.Trajectory(obs=observations7, acts=actions7, infos=None, terminal=True)
# tes8 = types.Trajectory(obs=observations8, acts=actions8, infos=None, terminal=True)
# tes9 = types.Trajectory(obs=observations9, acts=actions9, infos=None, terminal=True)
# tes10 = types.Trajectory(obs=observations10, acts=actions10, infos=None, terminal=True)

# print('tes')
# print(tes)

# transitions = rollout.flatten_trajectories([tes])
transitions = rollout.flatten_trajectories([tes])
# transitions = rollout.flatten_trajectories([tes, tes2, tes3, tes4, tes5, tes6, tes7, tes8, tes9, tes10])

# print('transitions')
# print(len(transitions))
# print(transitions)

obstacles_env = ObstaclesTrack(filedir)
vec_obstacles_env = make_vec_env(lambda: obstacles_env, n_envs=1)


print('vec_obstacles_env.observation_space')
print(vec_obstacles_env.observation_space)
print('vec_obstacles_env.action_space')
print(vec_obstacles_env.action_space)

customFeedForward = ActorCriticPolicy(
    observation_space=vec_obstacles_env.observation_space,
    action_space=vec_obstacles_env.action_space,
    # Set lr_schedule to max value to force error if policy.optimizer
    # is used by mistake (should use self.optimizer instead).
    lr_schedule=bc.ConstantLRSchedule(th.finfo(th.float32).max),
    net_arch=[nets_number,nets_number]
)

if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack" + tipo + "/logs/", ["stdout", "csv", "log", "tensorboard"])
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=vec_obstacles_env.observation_space,
        action_space=vec_obstacles_env.action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length,
        policy=customFeedForward   
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack" + tipo + "/bc_policy.zip")

    pol = bc.reconstruct_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack" + tipo + "/bc_policy.zip")

    # act = pol.predict([-0.8000004291534424,-0.6000002026557922,-1.5708264112472534])
    # act = pol.predict([-0.6685453057289124,-0.7484503388404846,-1.5713883638381958], deterministic=True)
    # print('act')
    # print(act)


else:

    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_obstacles_env.observation_space,
        action_space=vec_obstacles_env.action_space,
        hid_sizes= (nets_number,nets_number)
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrackwithSensor/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=976, n_steps=976, ent_coef=0.001, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" : [nets_number, nets_number]})
    # learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
    # learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


    bc_policy = gail.GAIL(
        venv=vec_obstacles_env,
        demonstrations=transitions,
        demo_batch_size=batch_length,
        gen_algo=learner,
        reward_net=gail_reward_net,
        custom_logger=gail_logger
    )


    # learner_rewards_before_training, _ = evaluate_policy(
    #     learner, vec_obstacles_env, 1, return_episode_rewards=True
    # )

    bc_policy.train(total_timesteps=total_epochs)

    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrack' + tipo + '/gail_policy.zip')





