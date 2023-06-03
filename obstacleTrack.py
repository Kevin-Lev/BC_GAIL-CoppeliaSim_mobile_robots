from time import sleep
from datetime import datetime, timedelta
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import writeSimulationData
import sys

client = RemoteAPIClient('localhost',23000)

sim = client.getObject('sim') # controle da simulação
# simOMPL = client.getObject('simOMPL') # Plugin ompl para motion planning

if sim:
    print("Conectado com o Coppelia Sim!")

if sim.getSimulationState()!=sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

loadedScene = ''

print('sys.argv[2]')
print(sys.argv[2])

if sys.argv[2] == '1':
    loadedScene = sim.loadScene('simulationScenes/epuck_obstacles_track_small_1.ttt')
    print('Carregou cena obstacles_track_small_1.ttt!')
elif sys.argv[2] == '2':
    loadedScene = sim.loadScene('simulationScenes/epuck_obstacles_track_small_2.ttt')
    print('Carregou cena obstacles_track_small_2.ttt!')
elif sys.argv[2] == '3':
    loadedScene = sim.loadScene('simulationScenes/epuck_obstacles_track_small_3.ttt')
    print('Carregou cena obstacles_track_small_3.ttt.ttt!')
else:
    loadedScene = sim.loadScene('simulationScenes/epuck_obstacles_track_small.ttt')
    print('Carregou cena obstacles_track_small.ttt!')

# if loadedScene != -1:
#     print('Carregou cena obstacles_track.ttt!')
# else:
#     print('falha ao tentar carregar cena!')

# Run a simulation in synchronous mode:
# client.setStepping(True)

epuck_handle = sim.getObjectHandle('ePuck')
epuck_position = sim.getObjectPosition(epuck_handle, -1)
init_x = 5
init_y = -6
pos_x = epuck_position[0]
pos_y = epuck_position[1]
left_motor_handle = sim.getObjectHandle('ePuck_leftJoint')
right_motor_handle = sim.getObjectHandle('ePuck_rightJoint')

print('pos_x')
print(pos_x)
print('pos_y')
print(pos_y)
print('init_x')
print(init_x)
print('init_y')
print(init_y)

print(int(pos_x))

sim.startSimulation() #Executa a simulação

# timeBegin = datetime.now()
# timeEnd = timeBegin + timedelta(minutes = 3, seconds=50)

while int(pos_x) != init_x or int(pos_y) != init_y:
    epuck_position = sim.getObjectPosition(epuck_handle, -1)
    epuck_orientation = sim.getObjectOrientation(epuck_handle, -1)
    jointSpeeds = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
    pos_x = epuck_position[0]
    pos_y = epuck_position[1]
    print(pos_x)
    print(pos_y)
    # timeBegin = datetime.now()
    # print('timeBegin')
    # print(timeBegin)
    # print('timeEnd')
    # print(timeEnd)
    writeSimulationData('epuck_obstacleTrack.txt', epuck_position, epuck_orientation, jointSpeeds, None, '')
    print('aguardando...')
    sleep(3)


# while timeBegin < timeEnd:
#     epuck_position = sim.getObjectPosition(epuck_handle, -1)
#     epuck_orientation = sim.getObjectOrientation(epuck_handle, -1)
#     jointSpeeds = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
#     # pos_x = epuck_position[0]
#     # pos_y = epuck_position[1]
#     timeBegin = datetime.now()
#     print('timeBegin')
#     print(timeBegin)
#     print('timeEnd')
#     print(timeEnd)
#     writeSimulationData('epuck_obstracleTrack.txt', epuck_position, epuck_orientation, jointSpeeds, None, '')
#     sleep(3)

sim.stopSimulation()