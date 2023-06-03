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
from obstacles_env_generalized import ObstaclesTrackGeneralized

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readEpuckDataImitation

total_epochs = int(sys.argv[1])
filedir1 = sys.argv[2]
filedir2 = sys.argv[3]
filedir3 = sys.argv[4]
imitation_method = sys.argv[5]
nets_number = int(sys.argv[6])


observations1, actions1, tipo1 = readEpuckDataImitation(filedir1)
observations2, actions2, tipo2 = readEpuckDataImitation(filedir2)
observations3, actions3, tipo3 = readEpuckDataImitation(filedir3)

print('TIPO')
print(tipo1)
print('Quantidade camada oculta:')
print(nets_number)

batch_length1 = len(observations1) - 1
observations1 = np.array(observations1, dtype=np.float32)
actions1 = np.array(actions1, dtype=np.float32)

batch_length2 = len(observations2) - 1
print('batch_length2')
print(batch_length2)
observation2 = np.array(observations2, dtype=np.float32)
actions2 = np.array(actions2, dtype=np.float32)

batch_length3 = len(observations3) - 1
observations3 = np.array(observations3, dtype=np.float32)
actions3 = np.array(actions3, dtype=np.float32)

print('batch_length1')
print(batch_length1)
print('imitation_method')
print(imitation_method)
# print(observations)
# print(actions)

tes1 = types.Trajectory(obs=observations1, acts=actions1, infos=None, terminal=True)
tes2 = types.Trajectory(obs=observations2, acts=actions2, infos=None, terminal=True)
tes3 = types.Trajectory(obs=observations3, acts=actions3, infos=None, terminal=True)

# print('tes')
# print(tes)

# transitions = rollout.flatten_trajectories([tes1, tes2])
transitions = rollout.flatten_trajectories([tes1, tes2, tes3])

# print('transitions')
# print(len(transitions))
# print(transitions)

obstacles_env = ObstaclesTrackGeneralized(filedir1, filedir2, filedir3)
# obstacles_env = ObstaclesTrackGeneralized(filedir1, filedir2, filedir3)
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
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrackGeneralized" + tipo1 + "/logs/", ["stdout", "csv", "log", "tensorboard"])
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=vec_obstacles_env.observation_space,
        action_space=vec_obstacles_env.action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length2,
        policy=customFeedForward    
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrackGeneralized" + tipo1 + "/bc_policy.zip")

    pol = bc.reconstruct_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrackGeneralized" + tipo1 + "/bc_policy.zip")

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

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrackwithSensor/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=117, n_steps=117, ent_coef=0.0, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" : [nets_number, nets_number]})
    # learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
    # learner = sb3.PPO("MlpPolicy", vec_obstacles_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


    bc_policy = gail.GAIL(
        venv=vec_obstacles_env,
        demonstrations=transitions,
        demo_batch_size=117,
        gen_algo=learner,
        reward_net=gail_reward_net,
        custom_logger=gail_logger
    )


    # learner_rewards_before_training, _ = evaluate_policy(
    #     learner, vec_obstacles_env, 1, return_episode_rewards=True
    # )

    bc_policy.train(total_timesteps=total_epochs)

    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrackGeneralized' + tipo1 + '/gail_policy.zip')





