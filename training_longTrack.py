import sys
import numpy as np
from gym import spaces
from imitation.data import rollout
from imitation.data import types
from imitation.util import logger, util
from imitation.algorithms import bc
from simulationScripts.file import readDataImitation

total_epochs = int(sys.argv[1])

# observations, actions = readDataImitation('simulationData/pioneerLongTrack/pioneer_longTrack_24_2_2022_testesbc.txt')

observations, actions = readDataImitation('simulationData/pioneerLongTrack/pioneer_longTrack_6_3_2022_testebc2.txt')

# observations.append([5.024043083190918, 3.3925983905792236, -0.013310858979821205])
observations.append([5.016650676727295, 3.2497057914733887, -0.042145781219005585])

print(observations)
print(actions)

observations = np.array(observations, dtype=np.float32)
actions = np.array(actions, dtype=np.float32)

tes = types.Trajectory(obs=observations, acts=actions, infos=None, terminal=True)

transitions = rollout.flatten_trajectories([tes])

print('tes')
print(tes)

print('transitions')
print(len(transitions))
print(transitions[0])
print(transitions[1])
print(transitions[21])

# Pos x:  max: +7.2055   min: -7.1195
# Pos y:  max: +4.7250   min: -4.7250
# ori     max: +3.141592 min: -3.141592
#wheel_speed max: 2.0    min: 0.0

obs_lows = np.array([-7.1195e+00, -4.7250e+00, -3.141592], dtype=np.float32)
obs_highs = np.array([7.1195e+00, 4.7250e+00, 3.141592], dtype=np.float32)
act_lows = np.array([0.0, 0.0], dtype=np.float32) 
act_highs = np.array([2.0, 2.0], dtype=np.float32) 

observation_space = spaces.Box(low=obs_lows, high=obs_highs, dtype=np.float32)

action_space = spaces.Box(low=act_lows, high=act_highs, dtype=np.float32)

print('observation_space')
print(observation_space)
print('action_space')
print(action_space)

bc_logger = logger.configure("/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneer/logs/")
# bc_logger = logger.configure(tempdir_path / "BC/")
bc_trainer = bc.BC(
    observation_space=observation_space,
    action_space=action_space,
    demonstrations=transitions,
    custom_logger=bc_logger,
    batch_size=28
)
bc_trainer.train(n_epochs=total_epochs, progress_bar=True)

bc_trainer.save_policy('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneer/bc_policy.zip')