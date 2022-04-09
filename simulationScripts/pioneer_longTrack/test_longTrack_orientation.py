from datetime import datetime
from time import sleep
import numpy as np
import sys
import stable_baselines3 as sb3
from stable_baselines3 import PPO
from zmqRemoteApi import RemoteAPIClient
from imitation.algorithms import bc
from imitation.algorithms.adversarial import gail
from imitation.rewards import reward_nets
from stable_baselines3.common.env_util import make_vec_env
from imitation.data import rollout, types
from gym import spaces
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import formatObservation, readDataImitation, writeSimulationData
from longTrack_env import LongTrack

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

    loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/pioneer_longTrack_noSensor.ttt')

    if loadedScene != -1:
        print('Carregou cena pioneer_longTrack.ttt!')
    else:
        print('falha ao tentar carregar cena!')

    # Run a simulation in synchronous mode:
    # client.setStepping(True)

    now = datetime.now()
    today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

    if sys.argv[2] == '1':
        print('Behavioral Cloning selecionada para as predições!')
        imitation_policy = bc.reconstruct_policy('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/pioneerLongtrackwithOrientation/bc_policy.zip')
        fileDirectory = 'simulationData/pioneerLongTrack/withOrientation/test/BC/' + today_date + '/pioneer_longTrack_' + str(i) + '.txt'
    else:
        print('GAIL selecionada para as predições!')
        imitation_policy = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/pioneerLongtrackwithOrientation/gail_policy.zip')
        fileDirectory = 'simulationData/pioneerLongTrack/withOrientation/test/GAIL/' + today_date + '/pioneer_longTrack_' + str(i) + '.txt'

    

    sim.startSimulation() #Executa a simulação

    print('Simulação iniciada!')

    # handles iniciais
    pioneer_handle = sim.getObjectHandle('Pioneer_p3dx')
    left_motor_handle = sim.getObjectHandle('Pioneer_p3dx_leftMotor')
    right_motor_handle = sim.getObjectHandle('Pioneer_p3dx_rightMotor')
    orientation = sim.getObjectOrientation(pioneer_handle, -1)

    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_x = positions[0]
    pos_y = positions[1]

    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)

    # print('obs_data')
    # print(obs_data)
   
    # ativa os motores com velocidade 2.0
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    # pred = imitation_policy.predict(obs_data)
    pred = pred[0].tolist()
    # sim.setJointTargetVelocity(left_motor_handle, 2.0)
    # sim.setJointTargetVelocity(right_motor_handle, 2.0)
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))

    # Registra posição, orientação e velocidade das rodas no início
    initial_position = positions
    initial_orientation = orientation
    initial_joint_speed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, initial_position, initial_orientation, initial_joint_speed, None)


    xInt = int(pos_x)

    # Enquanto o robô anda, vai fazendo a leitura de sua posição
    while pos_x > -3:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        
        # Cada metro do eixo X percorrido é um checkpoint para se pegar dados da posição e orientação atuais
        if int(pos_x) <= xInt - 1:
            xInt = int(pos_x)
            checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(xInt + 1) + ' y: ' + str(positions[1])
            orientation = sim.getObjectOrientation(pioneer_handle, -1)
            jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
            print(checkInfo)

            # writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )
            print('\n')


    # Momento de rotação do robô, diminuindo a velocidade do motor referente a direção desejada
    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    # orientation[2] = abs(orientation[2])
    # jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
    print(positions[0])
    print(positions[1])
    print('orientation[2] before')
    print(orientation[2])
    orientation[2] = abs(orientation[2])
    print('orientation[2]')
    print(orientation[2])
    # if orientation[2] < 0:
    #     print('orientation[2] before')
    #     print(orientation[2])
    #     orientation[2] = -orientation[2]
    #     print('orientation[2]')
    #     print(orientation[2])

    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)
    # pred = imitation_policy.predict(obs_data)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    pred = pred[0].tolist()
    print('pred IJIJI')
    print(pred)
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )

    y = positions[1]
    # print(orientation)
    gamma_angle = orientation[2]

    if gamma_angle > 0:
        gamma_angle = 0

    while gamma_angle <= 0:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]

    while gamma_angle >= 1.6:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]


    print('acabou tempo')

    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_y = positions[1]
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)
    # pred = imitation_policy.predict(obs_data)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )


    yInt = int(pos_y)
    while y < 3:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        y = positions[1]
        if int(y) > yInt:
            yInt = int(y)
            checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(xInt + 1) + ' y: ' + str(positions[1])
            print(checkInfo)
            orientation = sim.getObjectOrientation(pioneer_handle, -1)
            jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

            # writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )
            print('\n')


    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    print(positions[0])
    print(positions[1])
    print(orientation[2])
    # orientation[2] = abs(orientation[2])
    # gamma_angle = orientation[2]
    # if -1 < orientation[2] <= -0.0:
    #     print('orientation[2] before')
    #     print(orientation[2])
    #     orientation[2] = -orientation[2]
    #     print('orientation[2]')
    #     print(orientation[2])

    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)
    # pred = imitation_policy.predict(obs_data)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    # print('orientation[2]')
    # print(orientation[2])
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))

    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )

    pos_x = positions[0]
    pos_y = positions[1]

    while gamma_angle >= -0.0:
        orientation = sim.getObjectOrientation(pioneer_handle, -1)
        gamma_angle = orientation[2]
        # print('gamma_angle')
        # print(gamma_angle)

    print('acabou2')

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    
    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)
    # pred = imitation_policy.predict(obs_data)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))

    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )

    while pos_x < 5:
        positions = sim.getObjectPosition(pioneer_handle, -1)
        pos_x = positions[0]
        if int(pos_x) > xInt:
            xInt = int(pos_x)
            checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(xInt + 1) + ' y: ' + str(positions[1])
            print(checkInfo)
            orientation = sim.getObjectOrientation(pioneer_handle, -1)
            jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

            # writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )
            print('\n')
        

    positions = sim.getObjectPosition(pioneer_handle, -1)
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    
    # obs_data = formatObservation(positions[0], positions[1], orientation[2], None)
    # pred = imitation_policy.predict(obs_data)
    pred = imitation_policy.predict([positions[0], positions[1], orientation[2]])
    pred = pred[0].tolist()
    sim.setJointTargetVelocity(left_motor_handle, pred[0])
    sim.setJointTargetVelocity(right_motor_handle, pred[1])
    print("Velocidade das rodas prevista: " + str(pred[0]) + " " + str(pred[1]))
    jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]

    writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, None )


    sim.stopSimulation()

    # If you need to make sure we really stopped:
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

    # sim.closeScene()

