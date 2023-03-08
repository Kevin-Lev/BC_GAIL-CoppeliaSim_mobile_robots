from datetime import datetime
from time import sleep
import sys

from stable_baselines3 import PPO
from imitation.algorithms import bc
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import writeSimulationData


client = RemoteAPIClient('localhost',23000)

sim = client.getObject('sim') # controle da simulação
# simOMPL = client.getObject('simOMPL') # Plugin ompl para motion planning

if sim:
    print("Conectado com o Coppelia Sim!")
    
qnt_simulacoes = int(sys.argv[1])

for i in range(qnt_simulacoes):
    if sim.getSimulationState()!=sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState()!=sim.simulation_stopped:
            sleep(0.1)

    loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/pioneer_mTrack.ttt')

    if loadedScene != -1:
        print('Carregou cena pioneer_mTrack.ttt!')
    else:
        print('falha ao tentar carregar cena!')


    print('Iniciando a simulação ' + str(i) + '!')

    now = datetime.now()
    today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

    if sys.argv[2] == '1':
        print('Behavioral Cloning selecionada para as predições!')
        imitation_policy = bc.reconstruct_policy('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerMTrackwithOrientation/bc_policy.zip')
        fileDirectory = 'simulationData/pioneerMTrack/test/BC/' + today_date + '/pioneer_mTrack_' + str(i) + '.txt'
    else:
        print('GAIL selecionada para as predições!')
        imitation_policy = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerMTrack/gail_policy.zip')
        # imitation_policy = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerMTrack/gail_policy.zip')
        fileDirectory = 'simulationData/pioneerMTrack/test/GAIL/' + today_date + '/pioneer_mTrack_' + str(i) + '.txt'

    # fileDirectory = 'simulationData/pioneerMTrack/training/' + today_date + '/pioneer_mTrack_' + str(i) + '.txt'

    sim.startSimulation() #Executa a simulação

    print('Simulação iniciada!')

    pioneer_handle = sim.getObjectHandle('Pioneer_p3dx')
    left_motor_handle = sim.getObjectHandle('Pioneer_p3dx_leftMotor')
    right_motor_handle = sim.getObjectHandle('Pioneer_p3dx_rightMotor')
    orientation = sim.getObjectOrientation(pioneer_handle, -1)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_x = positions[0]
    pos_y = positions[1]

    print('pos_x')
    print(pos_x)

    # ativa os motores com velocidade 2.0
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))

    initial_position = positions
    initial_orientation = orientation
    initial_joint_speed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, initial_position, initial_orientation, initial_joint_speed, None)

    yInt = int(pos_y)

    # Enquanto o robô anda, vai fazendo a leitura de sua posição
    while pos_y > -4:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_y = positions[1]
        
        # Cada metro do eixo X percorrido é um checkpoint para se pegar dados da posição e orientação atuais
        if int(pos_y) <= yInt - 1:
            yInt = int(pos_y)
            checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(positions[0]) + ' y: ' + str(yInt + 1)
            orientation = sim.getObjectOrientation(pioneer_handle, -1)
            jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
            print(checkInfo)
            
            # writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None)
            print('\n')

    
    # Momento de rotação do robô, diminuindo a velocidade do motor referente a direção desejada
    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    # orientation[2] = abs(orientation[2])
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None)

    gamma_angle = orientation[2]

    if gamma_angle > 0:
        gamma_angle = 0

    print('gamma_angle')
    print(gamma_angle)
    print('jointsSpeed')
    print(jointsSpeed)

    # while gamma_angle != 1.39:
    while float(format(gamma_angle, ".2f")) != 2.45:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_y = positions[1]
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None)


    xInt = int(pos_x)
    yInt = int(pos_y)
    print('pos_x')
    print(pos_x)
    print('pos_y')
    print(pos_y)

    while float(format(pos_x, '.2f')) >= 0.40:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

        # writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)
        # print('pos_x')
        # print(pos_x)
        # print('pos_y')
        # print(pos_y)

    # ROBÔ CHEGOU NO CENTRO DO MAPA
    checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(positions[0]) + ' y: ' + str(positions[1])
    print(checkInfo)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    # orientation[2] = abs(orientation[2])
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None)

    gamma_angle = orientation[2]

    while float(format(gamma_angle, ".2f")) != -2.30:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None)

    while float(format(pos_x, '.2f')) >= -3.95:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

        # print('pos_x')
        # print(pos_x)
        # print('pos_y')
        # print(pos_y)

    # ROBO CHEGOU NO CANTO SUPERIOR DIREITO
    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    while float(format(gamma_angle, ".2f")) != 1.65:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)


    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    while float(format(pos_y, '.2f')) <= 3.30:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

        # print('pos_x')
        # print(pos_x)
        # print('pos_y')
        # print(pos_y)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    #CHEGOU CANTO INFERIOR DIREITO
    while float(format(gamma_angle, ".2f")) != -0.6:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    while float(format(pos_x, '.2f')) <= -0.35:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

        # print('pos_x')
        # print(pos_x)
        # print('pos_y')
        # print(pos_y)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    while float(format(gamma_angle, ".2f")) != 0.50:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    while float(format(pos_x, '.2f')) <= 5.70:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

        # print('pos_x')
        # print(pos_x)
        # print('pos_y')
        # print(pos_y)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]], deterministic=True)
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    # sleep(3)

    writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, None)

    sim.stopSimulation()

    # If you need to make sure we really stopped:
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

    # sim.closeScene()

    print('--------------------------------------------------------')
    print('\n')