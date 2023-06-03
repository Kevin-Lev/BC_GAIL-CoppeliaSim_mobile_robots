from datetime import datetime
from time import sleep
import sys, numpy as np
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import separateSensorAndAction, writeEpuckPosition, writeEpuckSimData, writeEpuckSimDataOnlyDistance, writeSimulationData

# np.set_printoptions(precision=4)

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

    loadedScene = ''
    if sys.argv[2] == '1':
        loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/epuck_obstacles_track_small_1.ttt')
        print('Carregou cena obstacles_track_small_1.ttt!')
    elif sys.argv[2] == '2':
        loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/epuck_obstacles_track_small_2.ttt')
        print('Carregou cena obstacles_track_small_2.ttt!')
    elif sys.argv[2] == '3':
        loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/epuck_obstacles_track_small_3.ttt')
        print('Carregou cena obstacles_track_small_3.ttt!')
    elif sys.argv[2] == '4':
        loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/epuck_obstacles_track_small_1_onlyDistanceSensor2.ttt')
        print('Carregou cena obstacles_track_small_1_onlyDistanceSensor2.ttt!')
    else:
        loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/epuck_obstacles_track_small.ttt')
        print('Carregou cena obstacles_track_small.ttt!')
    

    # if loadedScene != -1:
    #     print('Carregou cena epuck_obstacles_track_small.ttt!')
    # else:
    #     print('falha ao tentar carregar cena!')

    # Run a simulation in synchronous mode:
    # client.setStepping(True)

    print('Iniciando a simulação ' + str(i) + '!')

    now = datetime.now()
    today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

    fileDirectory = 'simulationData/epuckObstaclestrack/withSensor/training/' + today_date + '/epuck_obstaclesTrack_' + str(i) + '.txt'
    fileDirectory_pos = 'simulationData/epuckObstaclestrack/withSensor/training/' + today_date + '/epuck_obstacles_positions' + str(i) + '.txt'

    #handles iniciais
    epuck_handle = sim.getObjectHandle('ePuck')
    left_motor_handle = sim.getObjectHandle('ePuck_leftJoint')
    right_motor_handle = sim.getObjectHandle('ePuck_rightJoint')
    positions = sim.getObjectPosition(epuck_handle, -1)
    orientation = sim.getObjectOrientation(epuck_handle, -1)
    senHandles = []

    pos_x = positions[0]
    pos_y = positions[1]

    writeEpuckPosition(fileDirectory_pos, positions)

    for i in range(1, 9):
        print('ePuck_proxSen' + str(i))
        handle = sim.getObjectHandle('ePuck_proxSen' + str(i))
        senHandles.append(handle)
        
    print('senHandles: ', senHandles)

    sim.startSimulation() #Executa a simulação

    while float(format(pos_x, ".1f")) != 2.5 or float(format(pos_y, ".1f")) != -1.7:
        try:
            sleep(0.1)
            sensor_distances = []
            for handle in senHandles:
                sim.handleProximitySensor(handle)
                # print(sim.handleProximitySensor(handle))
                res = sim.readProximitySensor(handle)
                #    res = sim.handleProximitySensor(handle)
                # if handle == 'ePuck_proxSen4':
                # print('res: ', res[1])
                sensor_distances.append(res[1])
                #    print('dist: ', dist)
            positions = sim.getObjectPosition(epuck_handle, -1)
            pos_x = positions[0]
            pos_y = positions[1]
            l_wheel_speed = sim.getJointTargetVelocity(left_motor_handle)
            r_wheel_speed = sim.getJointTargetVelocity(right_motor_handle)
            print('sensor data: ', sensor_distances)
            print('wheels speed: ', l_wheel_speed, r_wheel_speed)
            # writeEpuckPosition(fileDirectory_pos, positions)
            # writeEpuckSimDataOnlyDistance(fileDirectory, sensor_distances , [l_wheel_speed, r_wheel_speed])
            print('---------------')
        except Exception as e:
            print('Erro! Ainda está aguardando o buffer...', e)


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

        


    # print('epuck_handle')
    # print(epuck_handle)
    # print('left_motor_handle')
    # print(left_motor_handle)
    # print('right_motor_handle')
    # print(right_motor_handle)
    # print('orientation')
    # print(orientation)
    # print('positions')
    # print(positions)

    # pos_x = positions[0]
    # pos_y = positions[1]

    # writeEpuckPosition(fileDirectory_pos, positions)
    
    # sim.startSimulation() #Executa a simulação

    # print('Simulação iniciada!')

    # print('Aguardando o e-puck começar a andar...')
    # sleep(3)
    # print('Pronto!!')

    # print('pos x atual: ' + str(positions[0]))
    # print('pos y atual: ' + str(positions[1]))
    # sleep(2)
    # i = 0

    # while float(format(pos_x, ".1f")) != 2.5 or float(format(pos_y, ".1f")) != -1.7:
    #     sleep(0.1)
    #     i += 1
    #     print('iteração atual: ' + str(i))
    #     try:
    #         sensor_and_wheel = sim.getStringSignal('sensor_and_wheel')
    #         sensor_and_wheel = sim.unpackTable(sensor_and_wheel)
    #         light_data, sensor_data, action_data = separateSensorAndAction(sensor_and_wheel[0])
    #         # print(type(light_data))
    #         # print(type(sensor_data))
    #         # print(type(action_data))
    #         # light_data = [np.float32(light_data[0][0]), np.float32(light_data[0][1]), np.float32(light_data[0][2])]
    #         # sensor_data = [np.float32(sensor_data[0]), np.float32(sensor_data[1]), np.float32(sensor_data[2]), np.float32(sensor_data[3]), np.float32(sensor_data[4]), np.float32(sensor_data[5]), np.float32(sensor_data[6]), np.float32(sensor_data[7])]
    #         # action_data = [np.float32(action_data[0]), np.float32(action_data[1])]
    #         # print(light_data)
    #         print(sensor_data)
    #         print(action_data)
    #         # light_data, sensor_data, action_data = np.float32(light_data), np.float32(sensor_data), np.float32(action_data)
    #         positions = sim.getObjectPosition(epuck_handle, -1)
    #         pos_x = positions[0]
    #         pos_y = positions[1]
    #         # print('float(format(pos_x, ".1f"))')
    #         # print(float(format(pos_x, ".1f")))
    #         # print('float(format(pos_y, ".1f"))')
    #         # print(float(format(pos_y, ".1f")))
    #         writeEpuckPosition(fileDirectory_pos, positions)
    #         writeEpuckSimDataOnlyDistance(fileDirectory, sensor_data, action_data)
    #         # writeEpuckSimData(fileDirectory, light_data, sensor_data, action_data)
    #     except Exception as e:
    #         print('Erro! Ainda está aguardando o buffer...', e)


    # print('PAROU')

    # sim.setJointTargetVelocity(left_motor_handle, 0.0)    
    # sim.setJointTargetVelocity(right_motor_handle, 0.0)    

    # sim.stopSimulation()

    # # If you need to make sure we really stopped:
    # while sim.getSimulationState()!=sim.simulation_stopped:
    #     sleep(0.1)

    # # sim.closeScene()

    # print('--------------------------------------------------------')
    # print('\n')