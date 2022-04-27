from turtle import position
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import readTrainAndTestActions, readTrainAndTestPositions, readEpuckTrainandTestPos
from simulationScripts.meanSquareError import calculate_loss, mean_loss_simulations, mean_squared_error


def plotIdealAndModelPaths(ideal_path, first_model_path, second_model_path):
    expected_positions, first_model_positions = readTrainAndTestPositions(ideal_path, first_model_path)
    _, second_model_positions = readTrainAndTestPositions(ideal_path, second_model_path)

    print('expected_positions')
    print(expected_positions)
    print('first_model_path')
    print(first_model_path)

    posesx_train = []
    posesy_train = []
    first_posesx_test = []
    first_posesy_test = []
    second_posesx_test = []
    second_posesy_test = []

    fig, (ax, ax2, ax3) = plt.subplots(ncols=3)
    ax.set_box_aspect(0.7)
    ax2.set_box_aspect(0.7)
    ax3.set_box_aspect(0.7)
    plt.title('Percurso ideal x percurso gerado pelos modelos')
    ax.set_title('Percurso ideal')
    ax2.set_title('Clonagem comportamental')
    ax3.set_title('GAIL')

    # Pos x:  max: +7.2055   min: -7.1195
    # Pos y:  max: +4.7250   min: -4.7250

    ax.set_xlim([-7.11, 7.11])
    ax.set_ylim([-4.725, 4.725])
    ax2.set_xlim([-7.11, 7.11])
    ax2.set_ylim([-4.725, 4.725])
    ax3.set_xlim([-7.11, 7.11])
    ax3.set_ylim([-4.725, 4.725])

    for i in range(len(expected_positions)):
        posesx_train.append(expected_positions[i][0])
        posesy_train.append(expected_positions[i][1])
        first_posesx_test.append(first_model_positions[i][0])
        first_posesy_test.append(first_model_positions[i][1])
        second_posesx_test.append(second_model_positions[i][0])
        second_posesy_test.append(second_model_positions[i][1])

    ax.plot(posesx_train, posesy_train)
    ax2.plot(first_posesx_test, first_posesy_test)
    ax3.plot(second_posesx_test, second_posesy_test)

    ax.invert_xaxis()
    ax.invert_yaxis()
    ax2.invert_xaxis()
    ax2.invert_yaxis()
    ax3.invert_xaxis()
    ax3.invert_yaxis()

    plt.show()


def plotIdealAndMeanModelPaths(ideal_path, first_model_path, second_model_path):
    expected_positions, first_model_positions = readTrainAndTestPositions(ideal_path, first_model_path)
    _, second_model_positions = readTrainAndTestPositions(ideal_path, second_model_path)

    print('expected_positions')
    print(expected_positions)
    print('first_model_path')
    print(first_model_path)

    posesx_train = []
    posesy_train = []
    first_posesx_test = []
    first_posesy_test = []
    second_posesx_test = []
    second_posesy_test = []

    fig, (ax, ax2, ax3) = plt.subplots(ncols=3)
    
    plt.title('Percurso ideal x 10 trajetórias geradas pela CC')
    ax.set_box_aspect(0.7)
    ax.set_title('Percurso ideal')
    ax2.set_box_aspect(0.7)
    ax2.set_title('Clonagem comportamental')
    ax3.set_box_aspect(0.7)
    ax3.set_title('GAIL')


    # Pos x:  max: +7.2055   min: -7.1195
    # Pos y:  max: +4.7250   min: -4.7250

    ax.set_xlim([-7.11, 7.11])
    ax.set_ylim([-4.725, 4.725])
    ax2.set_xlim([-7.11, 7.11])
    ax2.set_ylim([-4.725, 4.725])
    ax3.set_xlim([-7.11, 7.11])
    ax3.set_ylim([-4.725, 4.725])

    for i in range(len(expected_positions)):
        posesx_train.append(expected_positions[i][0])
        posesy_train.append(expected_positions[i][1])


    ax.plot(posesx_train, posesy_train)

    first_test_directory = first_model_path.split('pioneer_longTrack_')
    second_test_directory = second_model_path.split('pioneer_longTrack_')

    for j in range(10):
        expected_positions, first_model_positions = readTrainAndTestPositions(sys.argv[1], first_test_directory[0] + 'pioneer_longTrack_' + str(j) + '.txt')
        expected_positions, second_model_positions = readTrainAndTestPositions(sys.argv[1], second_test_directory[0] + 'pioneer_longTrack_' + str(j) + '.txt')
        for i in range(len(first_model_positions)):
            first_posesx_test.append(first_model_positions[i][0])
            first_posesy_test.append(first_model_positions[i][1])
            ax2.plot(first_posesx_test, first_posesy_test)

            second_posesx_test.append(second_model_positions[i][0])
            second_posesy_test.append(second_model_positions[i][1])
            ax3.plot(second_posesx_test, second_posesy_test)
        first_posesx_test = []
        first_posesy_test = []
        second_posesx_test = []
        second_posesy_test = []

    ax.invert_xaxis()
    ax.invert_yaxis()
    ax2.invert_xaxis()
    ax2.invert_yaxis()
    ax3.invert_xaxis()
    ax3.invert_yaxis()

    plt.show()

def plotMeanLoss(ideal_path, model_path):
    simulations = []

    mean_loss, loss_list = mean_loss_simulations(ideal_path, model_path)

    for i in range(1, len(loss_list) + 1):
        simulations.append(i)

    fig, ax = plt.subplots()
    plt.title('ErroQuadraticoMedioxSimulacao')

    ax.set_ylim([0.0, 1.0])
    ax.plot(simulations, loss_list)

    ax.set_xlabel('Simulação')
    ax.set_ylabel('Erro Quadrático Médio')

    plt.show()
    

# if sys.argv[4] == '1':
#     plotIdealAndModelPaths(sys.argv[1], sys.argv[2], sys.argv[3])
# elif sys.argv[4] == '2':
#     plotIdealAndMeanModelPaths(sys.argv[1], sys.argv[2], sys.argv[3])
# else:
#     plotMeanLoss(sys.argv[1], sys.argv[2])

if sys.argv[3] == '1':
    readEpuckTrainandTestPos(sys.argv[1], sys.argv[2])