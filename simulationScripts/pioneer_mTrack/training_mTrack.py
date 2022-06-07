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
from mTrack_env import MTrack

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

from simulationScripts.file import readDataImitation

total_epochs = int(sys.argv[1])
filedir = sys.argv[2]
imitation_method = sys.argv[3]

observations, actions, tipo = readDataImitation(filedir)

print('TIPO')
print(tipo)


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

print('observation_space')
print(observation_space)
print('action_space')
print(action_space)

if imitation_method == '1':
    bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerMTrack" + tipo + "/logs/")
    # bc_logger = logger.configure(tempdir_path / "BC/")


    bc_trainer = bc.BC(
        observation_space=observation_space,
        action_space=action_space,
        demonstrations=transitions,
        custom_logger=bc_logger,
        batch_size=batch_length     
    )
    bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

    bc_trainer.save_policy("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerMTrack" + tipo + "/bc_policy.zip")

    # /home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerMTrack

else:

    m_env = MTrack(filedir)
    vec_m_env = make_vec_env(lambda: m_env, n_envs=1)
    # vec_m_env = DummyVecEnv([lambda: m_env] * 8)

    # observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

    # action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

    print('vec_m_env.observation_space')
    print(vec_m_env.observation_space)
    print('vec_m_env.action_space')
    print(vec_m_env.action_space)


    gail_reward_net = reward_nets.BasicRewardNet(
        observation_space=vec_m_env.observation_space,
        action_space=vec_m_env.action_space
    )

    gail_logger = logger.configure('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerMTrack/logs/', ["stdout", "csv", "log", "tensorboard"])

    print('gail_reward_net')
    print(gail_reward_net)

    learner = sb3.PPO("MlpPolicy", vec_m_env, verbose=1, batch_size=60, n_steps=120, ent_coef=0.0, n_epochs=10, vf_coef=0.5)
    # learner = sb3.PPO("MlpPolicy", vec_m_env, verbose=1, batch_size=6, n_steps=6, ent_coef=0.01, n_epochs=6, vf_coef=0.2)
    # learner = sb3.PPO("MlpPolicy", vec_m_env, verbose=1, batch_size=3, n_steps=3, n_epochs=1)


    bc_policy = gail.GAIL(
        venv=vec_m_env,
        demonstrations=transitions,
        demo_batch_size=batch_length,
        gen_algo=learner,
        reward_net=gail_reward_net,
        custom_logger=gail_logger
    )


    bc_policy.train(total_timesteps=total_epochs)


    bc_policy.gen_algo.save('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerMTrack/gail_policy.zip')

    poseList = [
        [5.7555341720581055,3.8502583503723145,-1.5707428455352783], 
        [5.70271635055542,-4.04437780380249,-1.5777218341827393], 
        [4.950206279754639,-4.522993087768555,2.4371659755706787], 
        [0.351197212934494,-0.22879281640052795, 2.3899970054626465], 
        [-0.4619595408439636,-0.177271768450737,-2.285512924194336], 
        [-3.9801547527313232,-4.374104022979736, -2.2681288719177246],

        [-4.8902907371521,-4.2138190269470215, 1.6326655149459839],
        [-4.983366966247559,3.354684352874756,1.582658052444458],
        [-4.274195671081543,3.874596357345581, -0.6116354465484619],
        [-0.3159048855304718,0.972848117351532, -0.6333227753639221],
        [0.24646306037902832,0.8809928894042969, 0.5140541195869446],
        [5.737455368041992,4.0756402015686035, 0.5273972749710083]
    ]

    for pose in poseList:
        pred = bc_policy.policy.predict(pose, deterministic=True)
        print(pose)
        print(pred)





