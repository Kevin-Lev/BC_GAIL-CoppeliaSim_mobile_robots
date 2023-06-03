import sys
from imitation.algorithms import bc
from stable_baselines3 import PPO
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import readEpuckDataImitation, readTrainAndTestActions
from simulationScripts.meanSquareError import calculate_mae, calculate_mse

def calc(ideal_path, model_path):
    expected_actions, predicted_actions = readTrainAndTestActions(ideal_path, model_path)

    calculate_mse(expected_actions, predicted_actions)
    calculate_mae(expected_actions, predicted_actions)


def readEpuckSensorActions(ideal_path, trainedModel_path, model_type):
    ideal_obs, expected_acts, _ = readEpuckDataImitation(ideal_path)
    if model_type == '1':
        print('BC selecionada!')
        imitation_policy = bc.reconstruct_policy(trainedModel_path)
    else:
        imitation_policy = PPO.load(trainedModel_path)
    # imitation_policy = PPO.load(trainedModel_path)
    predicted_acts = []

    # print('ideal_obs')
    # print(ideal_obs)

    for observation in ideal_obs:
        pred = imitation_policy.predict(observation=observation, deterministic=True)
        pred = pred[0].tolist()
        predicted_acts.append(pred)

    predicted_acts.pop()
    # print('expected_acts')
    # print(expected_acts)
    # print('predicted_acts')
    # print(predicted_acts)
    calculate_mse(expected_acts, predicted_acts)
    calculate_mae(expected_acts, predicted_acts)

# calc(sys.argv[1], sys.argv[2])
readEpuckSensorActions(sys.argv[1], sys.argv[2], sys.argv[3])