from datetime import datetime
from time import sleep
import sys
import stable_baselines3 as sb3
from stable_baselines3 import PPO
from imitation.algorithms import bc
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import separateSensorAndAction, writeEpuckPosition, writeEpuckSimData


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


    loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/e_puck_trajetoria_circular_test.ttt')

    if loadedScene != -1:
        print('Carregou cena e_puck_trajetoria_circular_sem_script.ttt!')
    else:
        print('falha ao tentar carregar cena!')

    # Run a simulation in synchronous mode:
    # client.setStepping(True)

    print('Iniciando a simulação ' + str(i) + '!')

    now = datetime.now()
    today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

    if sys.argv[2] == '1':
        print('Behavioral Cloning selecionada para as predições!')
        imitation_policy = bc.reconstruct_policy('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckCircletrackwithSensor/bc_policy.zip')
        # imitation_policy = bc.reconstruct_policy('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/BC/epuckObstaclestrackwithSensor_poucaAmostra/bc_policy.zip')
        fileDirectory = 'simulationData/epuckCircletrack/withSensor/test/BC/' + today_date + '/epuck_circleTrack_' + str(i) + '.txt'
        fileDirectory_pos = 'simulationData/epuckCircletrack/withSensor/test/BC/' + today_date + '/epuck_circle_positions_' + str(i) + '.txt'
    else:
        print('GAIL selecionada para as predições!')
        imitation_policy = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckCircletrackwithSensor/gail_policy.zip')
        # imitation_policy = PPO.load('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationData/GAIL/epuckObstaclestrackwithSensor_poucasAmostras/gail_policy.zip')
        fileDirectory = 'simulationData/epuckCircletrack/withSensor/test/GAIL/' + today_date + '/epuck_circleTrack_' + str(i) + '.txt'
        fileDirectory_pos = 'simulationData/epuckCircletrack/withSensor/test/GAIL/' + today_date + '/epuck_circle_positions_' + str(i) + '.txt'

    # fileDirectory = 'simulationData/epuckCircle/withSensor/test/' + today_date + '/epuck_circle_' + str(i) + '.txt'
    # fileDirectory_pos = 'simulationData/epuckCircle/withSensor/test/' + today_date + '/epuck_circle_positions' + str(i) + '.txt'

    #handles iniciais
    epuck_handle = sim.getObjectHandle('ePuck')
    left_motor_handle = sim.getObjectHandle('ePuck_leftJoint')
    right_motor_handle = sim.getObjectHandle('ePuck_rightJoint')
    positions = sim.getObjectPosition(epuck_handle, -1)
    orientation = sim.getObjectOrientation(epuck_handle, -1)

    pos_x = positions[0]
    pos_y = positions[1]

    writeEpuckPosition(fileDirectory_pos, positions)
    
    sim.startSimulation() #Executa a simulação

    print('Simulação iniciada!')

    print('pos x atual: ' + str(positions[0]))
    print('pos y atual: ' + str(positions[1]))
    # sleep(2)
    i = 0

    while float(format(pos_x, ".1f")) != -0.7 or float(format(pos_y, ".1f")) != -0.7:
        sleep(0.1)
        i += 1
        print('iteração atual: ' + str(i))
        try:
            sensor_and_wheel = sim.getStringSignal('sensor_and_wheel')
            sensor_and_wheel = sim.unpackTable(sensor_and_wheel)
            light_data, sensor_data, act = separateSensorAndAction(sensor_and_wheel[0])
            positions = sim.getObjectPosition(epuck_handle, -1)
            pos_x = positions[0]
            pos_y = positions[1]
            pred = imitation_policy.predict([light_data[0][0], light_data[0][1], light_data[0][2], sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3], sensor_data[4], sensor_data[5], sensor_data[6], sensor_data[7]], deterministic=True)
            print('pred')
            print(pred)
            pred = pred[0].tolist()
            sim.setJointTargetVelocity(left_motor_handle, pred[0])    
            sim.setJointTargetVelocity(right_motor_handle, pred[1])   
            writeEpuckPosition(fileDirectory_pos, positions)
            writeEpuckSimData(fileDirectory, light_data, sensor_data, [pred[0], pred[1]])
        except:
            print('Erro! Ainda está aguardando o buffer...')
        

    print('PAROU')

    sim.setJointTargetVelocity(left_motor_handle, 0.0)    
    sim.setJointTargetVelocity(right_motor_handle, 0.0)  

    sim.stopSimulation()

    # If you need to make sure we really stopped:
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

    # sim.closeScene()

    print('--------------------------------------------------------')
    print('\n')