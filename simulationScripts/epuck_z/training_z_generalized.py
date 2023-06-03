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
from z_env import ZTrackGeneralized

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readEpuckDataImitation

total_epochs = int(sys.argv[1])
filedir1 = sys.argv[2]
# filedir2 = sys.argv[3]
# filedir3 = sys.argv[4]
imitation_method = sys.argv[3]
nets_number = int(sys.argv[4])


observations1, actions1, tipo1 = readEpuckDataImitation(filedir1)
# observations2, actions2, tipo2 = readEpuckDataImitation(filedir2)
# observations3, actions3, tipo3 = readEpuckDataImitation(filedir3)

print('TIPO')
print(tipo1)
print('Quantidade camada oculta:')
print(nets_number)

batch_length1 = len(observations1) - 1
observations1 = np.array(observations1, dtype=np.float32)
actions1 = np.array(actions1, dtype=np.float32)

# batch_length2 = len(observations2) - 1
# observation2 = np.array(observations2, dtype=np.float32)
# actions2 = np.array(actions2, dtype=np.float32)

# batch_length3 = len(observations3) - 1
# observations3 = np.array(observations3, dtype=np.float32)
# actions3 = np.array(actions3, dtype=np.float32)

# print('batch_length3')
# print(batch_length3)
# print(observations)
# print(actions)

tes1 = types.Trajectory(obs=observations1, acts=actions1, infos=None, terminal=True)
# tes2 = types.Trajectory(obs=observations2, acts=actions2, infos=None, terminal=True)
# tes3 = types.Trajectory(obs=observations3, acts=actions3, infos=None, terminal=True)

# print('tes')
# print(tes)

transitions = rollout.flatten_trajectories([tes1])
# transitions = rollout.flatten_trajectories([tes1, tes2, tes3])

# print('transitions')
# print(len(transitions))
# print(transitions)

z_env = ZTrackGeneralized(filedir1)
# z_env = ZTrackGeneralized(filedir1, filedir2, filedir3)
vec_z_env = make_vec_env(lambda: z_env, n_envs=1)


print('vec_z_env.observation_space')
print(vec_z_env.observation_space)
print('vec_z_env.action_space')
print(vec_z_env.action_space)

customFeedForward = ActorCriticPolicy(
    observation_space=vec_z_env.observation_space,
    action_space=vec_z_env.action_space,
    # Set lr_schedule to max value to force error if policy.optimizer
    # is used by mistake (should use self.optimizer instead).
    lr_schedule=bc.ConstantLRSchedule(th.finfo(th.float32).max),
    net_arch=[nets_number,nets_number]
)

if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckZtrack" + tipo1 + "/logs/", ["stdout", "csv", "log", "tensorboard"])
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=vec_z_env.observation_space,
        action_space=vec_z_env.action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length1,
        # batch_size=batch_length1 + batch_length2 + batch_length3,
        policy=customFeedForward    
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckZtrack" + tipo1 + "/bc_policy.zip")

    pol = bc.reconstruct_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckZtrack" + tipo1 + "/bc_policy.zip")

else:

    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_z_env.observation_space,
        action_space=vec_z_env.action_space,
        hid_sizes= (nets_number,nets_number)
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckZtrackwithSensor/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_z_env, verbose=1, batch_size=64, n_steps=2048, ent_coef=0.001, n_epochs=10, vf_coef=0.5, policy_kwargs={"net_arch" : [nets_number, nets_number]})
    # learner = sb3.PPO("MlpPolicy", vec_z_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
    # learner = sb3.PPO("MlpPolicy", vec_z_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


    bc_policy = gail.GAIL(
        venv=vec_z_env,
        demonstrations=transitions,
        demo_batch_size=batch_length1,
        gen_algo=learner,
        reward_net=gail_reward_net,
        custom_logger=gail_logger
    )


    # learner_rewards_before_training, _ = evaluate_policy(
    #     learner, vec_z_env, 1, return_episode_rewards=True
    # )

    bc_policy.train(total_timesteps=total_epochs)

    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckZtrack' + tipo1 + '/gail_policy.zip')





