import sys
from turtle import circle
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

from simulationScripts.file import readEpuckDataImitation

total_epochs = int(sys.argv[1])
filedir = sys.argv[2]
imitation_method = sys.argv[3]
nets_number = int(sys.argv[4])

observations, actions, tipo = readEpuckDataImitation(filedir)

print('TIPO')
print(tipo)
print('Quantidade camada oculta:')
print(nets_number)

batch_length = len(observations) - 1
observations = np.array(observations, dtype=np.float32)
actions = np.array(actions, dtype=np.float32)

print('batch_length')
print(batch_length)
# print(observations)
# print(actions)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

# print('tes')
# print(tes)

transitions = rollout.flatten_trajectories([tes])

# print('transitions')
# print(len(transitions))
# print(transitions)

obstacles_env = ObstaclesTrack(filedir)
vec_obstacles_env = make_vec_env(lambda: obstacles_env, n_envs=1)

customFeedForward = ActorCriticPolicy(
    observation_space=vec_obstacles_env.observation_space,
    action_space=vec_obstacles_env.action_space,
    # Set lr_schedule to max value to force error if policy.optimizer
    # is used by mistake (should use self.optimizer instead).
    lr_schedule=bc.ConstantLRSchedule(th.finfo(th.float32).max),
    net_arch=[nets_number,nets_number]
)

print('vec_obstacles_env.observation_space')
print(vec_obstacles_env.observation_space)
print('vec_obstacles_env.action_space')
print(vec_obstacles_env.action_space)


if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack_semobstaculo" + tipo + "/logs/", ["stdout", "csv", "log", "tensorboard"])
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

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack_semobstaculo" + tipo + "/bc_policy.zip")

    pol = bc.reconstruct_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrack_semobstaculo" + tipo + "/bc_policy.zip")

    # act = pol.predict([-0.8000004291534424,-0.6000002026557922,-1.5708264112472534])
    # act = pol.predict([-0.6685453057289124,-0.7484503388404846,-1.5713883638381958], deterministic=True)
    # print('act')
    # print(act)


else:

    # obstacles_env = ObstaclesTrack()
    # vec_obstacles_env = make_vec_env(lambda: obstacles_env, n_envs=1)
    

    # print('vec_obstacles_env.observation_space')
    # print(vec_obstacles_env.observation_space)
    # print('vec_obstacles_env.action_space')
    # print(vec_obstacles_env.observation_space)


    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_obstacles_env.observation_space,
        action_space=vec_obstacles_env.action_space,
        hid_sizes= (nets_number,nets_number)
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrack_semobstaculowithSensor/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=219, n_steps=438, ent_coef=0.001, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" : [nets_number, nets_number]})
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

    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrack_semobstaculo' + tipo + '/gail_policy.zip')





