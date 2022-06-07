import matplotlib.pyplot as plt
import sys

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.meanSquareError import mean_loss_simulations
from simulationScripts.file import readSinglePositions

filepath = sys.argv[1]
nome_grafico = sys.argv[2]


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
    ax.set_title(nome_grafico)
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

    ax.plot(posesx_train, posesy_train)

    ax.invert_xaxis()
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