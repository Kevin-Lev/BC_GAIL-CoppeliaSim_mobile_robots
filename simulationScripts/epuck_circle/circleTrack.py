from datetime import datetime
from time import sleep
import sys
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import separateSensorAndAction, writeEpuckPosition, writeEpuckSimData, writeSimulationData


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


    loadedScene = sim.loadScene('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots/simulationScenes/e_puck_trajetoria_circular.ttt')

    if loadedScene != -1:
        print('Carregou cena e_puck_trajetoria_circular.ttt!')
    else:
        print('falha ao tentar carregar cena!')

    # Run a simulation in synchronous mode:
    # client.setStepping(True)

    print('Iniciando a simulação ' + str(i) + '!')

    now = datetime.now()
    today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)

    fileDirectory = 'simulationData/epuckCircletrack/withSensor/training/' + today_date + '/epuck_circleTrack_' + str(i) + '.txt'
    fileDirectory_pos = 'simulationData/epuckCircletrack/withSensor/training/' + today_date + '/epuck_circle_positions_' + str(i) + '.txt'

    #handles iniciais
    epuck_handle = sim.getObjectHandle('ePuck')
    left_motor_handle = sim.getObjectHandle('ePuck_leftJoint')
    right_motor_handle = sim.getObjectHandle('ePuck_rightJoint')
    positions = sim.getObjectPosition(epuck_handle, -1)
    orientation = sim.getObjectOrientation(epuck_handle, -1)

    print('epuck_handle')
    print(epuck_handle)
    print('left_motor_handle')
    print(left_motor_handle)
    print('right_motor_handle')
    print(right_motor_handle)
    print('orientation')
    print(orientation)
    print('positions')
    print(positions)

    pos_x = positions[0]
    pos_y = positions[1]

    writeEpuckPosition(fileDirectory_pos, positions)
    
    sim.startSimulation() #Executa a simulação

    print('Simulação iniciada!')

    # print('Aguardando o e-puck começar a andar...')
    # sleep(3)
    # print('Pronto!!')

    print('pos x atual: ' + str(positions[0]))
    print('pos y atual: ' + str(positions[1]))
    sleep(2)

    while float(format(pos_x, ".1f")) != -0.7 or float(format(pos_y, ".1f")) != -0.7:
        sensor_and_wheel = sim.getStringSignal('sensor_and_wheel')
        sensor_and_wheel = sim.unpackTable(sensor_and_wheel)
        light_data, sensor_data, action_data = separateSensorAndAction(sensor_and_wheel[0])
        positions = sim.getObjectPosition(epuck_handle, -1)
        pos_x = positions[0]
        pos_y = positions[1]
        writeEpuckPosition(fileDirectory_pos, positions)
        writeEpuckSimData(fileDirectory, light_data, sensor_data, action_data)

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