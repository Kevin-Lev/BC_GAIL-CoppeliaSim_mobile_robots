import sys
from typing import Callable
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
from longTrack_env import LongTrack
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.ppo.policies import MlpPolicy
from torch import nn
from stable_baselines3.common.type_aliases import Schedule

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readDataImitation

total_epochs = int(sys.argv[1])
filedir = sys.argv[2]
imitation_method = sys.argv[3]
nets_number = int(sys.argv[4])

observations, actions, tipo = readDataImitation(filedir)

print('TIPO')
print(tipo)
print('Quantidade camada oculta:')
print(nets_number)
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

obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
# obs_highs = np.array(highs_array, dtype=np.float32)
obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
act_lows = np.array([0.0, 0.0], dtype=np.float32) 
act_highs = np.array([2.0, 2.0], dtype=np.float32) 


observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

customFeedForward = ActorCriticPolicy(
    observation_space=observation_space,
    action_space=action_space,
    # Set lr_schedule to max value to force error if policy.optimizer
    # is used by mistake (should use self.optimizer instead).
    lr_schedule=bc.ConstantLRSchedule(th.finfo(th.float32).max),
    net_arch=[nets_number,nets_number]
)
# customFeedForward.net_arch = [64, 64]

print('observation_space')
print(observation_space)
print('action_space')
print(action_space)

print('customFeedForward')
print(customFeedForward)

if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrack" + tipo + "/logs/")
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=observation_space,
        action_space=action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length,
        policy=customFeedForward
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrack" + tipo + "/bc_policy.zip")

    poseList = [[5.755764961242676, -3.500044584274292, 3.1415629386901855], [-3.045706033706665,-3.4710705280303955, 3.1387693881988525], [-3.6208038330078125,-3.037193536758423, 1.5786396265029907], [-3.371680498123169,3.044665813446045,1.5291599035263062], [-2.9313392639160156, 3.5916759967803955, -0.021358318626880646], [5.020373344421387,3.2646336555480957,-0.042220111936330795]]

    print('Poses')
    for pose in poseList:
        pred = bc_trainer.policy.predict(pose, deterministic=True)
        print(pose)
        print(pred)

    # /home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrackwithOrientation

else:

    long_env = LongTrack(filedir)
    vec_long_env = make_vec_env(lambda: long_env, n_envs=1)
    # vec_long_env = DummyVecEnv([lambda: long_env] * 8)

    # observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

    # action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

    print('vec_long_env.observation_space')
    print(vec_long_env.observation_space)
    print('vec_long_env.action_space')
    print(vec_long_env.observation_space)


    # gail_reward_net = reward_nets.BasicShapedRewardNet(
    #     observation_space=vec_long_env.observation_space,
    #     action_space=vec_long_env.action_space,
    #     reward_hid_sizes=(nets_number,),
    #     potential_hid_sizes= ()
    # )

    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_long_env.observation_space,
        action_space=vec_long_env.action_space,
        hid_sizes= (nets_number,nets_number)
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    # batch size is nothing but, how many data points will be passed through the neural network (Fig-6) in one batch at a time
    # the batch size is a hyperparameter that defines the number of samples to work through before updating the internal model parameters.

    # Batch Gradient Descent. Batch Size = Size of Training Set
    # Stochastic Gradient Descent. Batch Size = 1
    # Mini-Batch Gradient Descent. 1 < Batch Size < Size of Training Set

    def linear_schedule(initial_value: float) -> Callable[[float], float]:
    
        def func(progress_remaining: float) -> float:
            """
            Progress will decrease from 1 (beginning) to 0.

            :param progress_remaining:
            :return: current learning rate
            """
            return progress_remaining * initial_value

        return func

    tes_mlp = MlpPolicy(observation_space=vec_long_env.observation_space, action_space=vec_long_env.action_space, lr_schedule=linear_schedule(0.001), activation_fn=nn.ReLU, net_arch=[dict(pi=[nets_number,nets_number], vf=[nets_number, nets_number])])

    # learner = sb3.PPO(tes_mlp, vec_long_env, verbose=1, batch_size=3, n_steps=96, ent_coef=0.0, n_epochs=10, vf_coef=0.5)
    # learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=64, n_steps=64, ent_coef=0.0, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" :  [nets_number, nets_number]})
    learner = sb3.PPO("MlpPolicy", vec_long_env, verbose=1, batch_size=3, n_steps=96, ent_coef=0.001, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" :  [dict(pi=[nets_number,nets_number], vf=[nets_number, nets_number])]})
    print('learner activation func')
    print(learner.policy)
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

    bc_policy.train(total_timesteps=total_epochs)


    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')

    poseList = [[5.755764961242676, -3.500044584274292, 3.1415629386901855], [-3.045706033706665,-3.4710705280303955, 3.1387693881988525], [-3.6208038330078125,-3.037193536758423, 1.5786396265029907], [-3.371680498123169,3.044665813446045,1.5291599035263062], [-2.9313392639160156, 3.5916759967803955, -0.021358318626880646], [5.020373344421387,3.2646336555480957,-0.042220111936330795]]

    print('Poses')
    for pose in poseList:
        pred = bc_policy.policy.predict(pose, deterministic=True)
        print(pose)
        print(pred)





