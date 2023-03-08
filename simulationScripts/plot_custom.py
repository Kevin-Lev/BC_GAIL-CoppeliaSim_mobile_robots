from turtle import color
import matplotlib.pyplot as plt
import sys
import numpy as np

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.meanSquareError import calculate_mae, calculate_mse, mean_loss_simulations
from simulationScripts.file import readSinglePositions, readTrainAndTestActions

filepath = sys.argv[1]
nome_grafico = sys.argv[2]

def plotLoss(ideal_path, bc_path, gail_path):
    fig, ax = plt.subplots()
    # plt.title('ErroQuadraticoMedioxSimulacao')
    labels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
    ax.set_xlabel('Cenários')
    ax.set_ylabel('Valor da média')

    #  Colocar for para varrer os ideal, bc e gail de cada cenário e jogar no gráfico de barra
    expected_actions, bc_predicted_actions = readTrainAndTestActions(ideal_path, bc_path)
    _, gail_predicted_actions = readTrainAndTestActions(ideal_path, gail_path)

    bc_mse = calculate_mse(expected_actions, bc_predicted_actions)
    bc_mae = calculate_mae(expected_actions, bc_predicted_actions)
    gail_mse = calculate_mse(expected_actions, gail_predicted_actions)
    gail_mae = calculate_mae(expected_actions, gail_predicted_actions)

    mse_list = [bc_mse, gail_mse]
    mae_list = [bc_mae, gail_mae]

    # ax.set_ylim([0.0, 1.0])
    ax.bar()
    ax.legend(['BC', 'GAIL'])

    ax.set_xlabel('Simulação')
    ax.set_ylabel('Erro Quadrático Médio BC x GAIL')


def plotAllPaths(ideal_path, bc_path, gail_path):
    ideal_positions = readSinglePositions(ideal_path)
    bc_positions = readSinglePositions(bc_path)
    gail_positions = readSinglePositions(gail_path)
    all_positions = [ideal_positions, bc_positions, gail_positions]
    posesx_ideal, posesy_ideal, posesx_bc, posesy_bc, posesx_gail, posesy_gail = [],[],[],[],[],[]

    fig, (ax) = plt.subplots(ncols=1)

    ax.set_xlim([-3.675, 3.675])
    ax.set_ylim([-2.4250, +2.4250])

    # ax.set_xlim([-7.11, 7.11])
    # ax.set_ylim([-4.7250, +4.7250])

    for i in range(len(ideal_positions)):
        posesx_ideal.append(ideal_positions[i][0])
        posesy_ideal.append(ideal_positions[i][1])

    for i in range(len(bc_positions)):
        posesx_bc.append(bc_positions[i][0])
        posesy_bc.append(bc_positions[i][1])

    for i in range(len(gail_positions)):
        posesx_gail.append(gail_positions[i][0])
        posesy_gail.append(gail_positions[i][1])

    ax.plot(posesx_ideal, posesy_ideal, color="black", label='Expert')
    ax.plot(posesx_bc, posesy_bc, color="blue", label='BC')
    ax.plot(posesx_gail, posesy_gail, color="red", label='GAIL')
    ax.legend()

    ax.invert_xaxis()
    ax.invert_yaxis()

    # Turn off tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])

    plt.show()


def plotErrorMetrics(err_file_path):
    file = open(err_file_path, 'r')
    data = file.read()
    print('data')
    data = data.splitlines()
    # print(data.splitlines())
    print(data)
    data_float = [float(d) for d in data]
    print('data_float')
    print(data_float)

    c1_metrics, c2_metrics, c3_metrics, c4_metrics = np.array_split(data_float, 4)

    print('c1_metrics, c2_metrics, c3_metrics, c4_metrics, ')
    print(c1_metrics, c2_metrics, c3_metrics, c4_metrics )

    fig, ax = plt.subplots()
    # ax.bar(x=['C1', 'C2', 'C3', 'C4', 'C5', 'C6'], height=20)
    cenarios = ['S1', 'S2', 'S3', 'S4']
    bc_mse_list = [c1_metrics[0], c2_metrics[0], c3_metrics[0], c4_metrics[0]]
    bc_mae_list = [c1_metrics[1], c2_metrics[1], c3_metrics[1], c4_metrics[1]]
    gail_mse_list = [c1_metrics[2], c2_metrics[2], c3_metrics[2], c4_metrics[2]]
    gail_mae_list = [c1_metrics[3], c2_metrics[3], c3_metrics[3], c4_metrics[3]]
    # Ygirls = [10,20,20,40, 50, 60]
    # Zboys = [20,30,25,30, 55, 78]

    X_axis = np.arange(len(cenarios))

    bars1 = ax.bar(X_axis - 0.3, bc_mse_list, 0.1, label = 'BC - MSE')
    bars2 = ax.bar(X_axis - 0.1, gail_mse_list, 0.1, label = 'GAIL - MSE')
    bars3 = ax.bar(X_axis + 0.1, bc_mae_list, 0.1, label = 'BC - MAE')
    bars4 = ax.bar(X_axis + 0.3, gail_mae_list, 0.1, label = 'GAIL - MAE')
    # plt.bar(X_axis - 0.2, Ygirls, 0.4, label = 'Girls')
    # plt.bar(X_axis + 0.2, Zboys, 0.4, label = 'Boys')
    # plt.bar(x='C1', height=15)

    ax.set_xticks(X_axis, cenarios)
    ax.set_xlabel('Scenarios', fontsize=18)
    ax.set_ylabel('Metric Value', fontsize=18)
    ax.bar_label(bars1, padding=6, fmt="%.5f", fontsize=12)
    ax.bar_label(bars2, padding=6, fmt="%.5f", fontsize=12)
    ax.bar_label(bars3, padding=6, fmt="%.5f", fontsize=12)
    ax.bar_label(bars4, padding=6, fmt="%.5f", fontsize=12)

    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
	    label.set_fontsize(14)

    plt.rcParams['font.size'] = '16'
    plt.legend(fontsize=18)
    plt.show()


def plotPath(ideal_path, nome_grafico):
    positions = readSinglePositions(ideal_path)
    # _, second_model_positions = readTrainAndTestPositions(ideal_path, second_model_path)

    print('positions')
    print(positions)

    posesx_train = []
    posesy_train = []

    fig, (ax) = plt.subplots(ncols=1)
    # ax.set_box_aspect(0.8)
    # plt.title('Percurso ideal x percurso gerado pelos modelos')
    
    # ax.set_title(nome_grafico)
    
    # ax3.set_title('GAIL')

    # Pos x:  max: +7.2055   min: -7.1195
    # Pos y:  max: +4.7250   min: -4.7250

    ax.set_xlim([-3.675, 3.675])
    ax.set_ylim([-2.4250, +2.4250])

    # ax.set_xlim([-7.11, 7.11])
    # ax.set_ylim([-4.7250, +4.7250])

    for i in range(len(positions)):
        posesx_train.append(positions[i][0])
        posesy_train.append(positions[i][1])

    ax.plot(posesx_train, posesy_train, color="black")

    # ax.invert_xaxis()
    ax.invert_yaxis()

    plt.show()

def plotMeanLoss(ideal_path, bc_path, gail_path):
    simulations = []

    bc_mean_loss, bc_loss_list = mean_loss_simulations(ideal_path, bc_path)
    gail_mean_loss, gail_loss_list = mean_loss_simulations(ideal_path, gail_path)

    print('bc_loss_list')
    print(bc_loss_list)
    print('gail_loss_list')
    print(gail_loss_list)

    for i in range(1, len(bc_loss_list) + 1):
        simulations.append(i)

    fig, ax = plt.subplots()
    plt.title('ErroQuadraticoMedioxSimulacao')

    ax.set_ylim([0.0, 0.02])
    ax.plot(simulations, bc_loss_list)
    ax.plot(simulations, gail_loss_list)
    ax.legend(['BC', 'GAIL'])

    ax.set_xlabel('Simulação')
    ax.set_ylabel('Erro Quadrático Médio BC x GAIL')

    # ax2.set_ylim([0.0, 0.2])
    # ax2.plot(simulations, gail_loss_list)

    # ax2.set_xlabel('Simulação')
    # ax2.set_ylabel('Erro Quadrático Médio GAIL')

    plt.show()


if (sys.argv[4] == '1'):
    plotPath(sys.argv[1], nome_grafico)
elif (sys.argv[4] == '2'):
    plotMeanLoss(sys.argv[1], sys.argv[2], sys.argv[3])
elif (sys.argv[4] == '3'):
    plotAllPaths(sys.argv[1], sys.argv[2], sys.argv[3])
elif (sys.argv[4] == '4'):
    plotErrorMetrics(sys.argv[1])
else:
    plotLoss(sys.argv[1], sys.argv[2], sys.argv[3])