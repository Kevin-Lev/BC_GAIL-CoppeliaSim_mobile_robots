from time import sleep
from datetime import datetime, timedelta
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import writeSimulationData

client = RemoteAPIClient('localhost',23000)

sim = client.getObject('sim') # controle da simulação
# simOMPL = client.getObject('simOMPL') # Plugin ompl para motion planning

if sim:
    print("Conectado com o Coppelia Sim!")

if sim.getSimulationState()!=sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

loadedScene = sim.loadScene('../cenas/e_puck_trajetoria_circular.ttt')

if loadedScene != -1:
    print('Carregou cena e_puck_trajetoria_circular.ttt!')
else:
    print('falha ao tentar carregar cena!')

# Run a simulation in synchronous mode:
# client.setStepping(True)

epuck_handle = sim.getObjectHandle('ePuck')
epuck_position = sim.getObjectPosition(epuck_handle, -1)
pos_x = epuck_position[0]
pos_y = epuck_position[1]
left_motor_handle = sim.getObjectHandle('ePuck_leftJoint')
right_motor_handle = sim.getObjectHandle('ePuck_rightJoint')

print('pos_x')
print(pos_x)
print('pos_y')
print(pos_y)

sim.startSimulation() #Executa a simulação
# sleep(3)
timeBegin = datetime.now()
timeEnd = timeBegin + timedelta(minutes = 3, seconds=50)

while timeBegin < timeEnd:
    epuck_position = sim.getObjectPosition(epuck_handle, -1)
    epuck_orientation = sim.getObjectOrientation(epuck_handle, -1)
    jointSpeeds = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
    # pos_x = epuck_position[0]
    # pos_y = epuck_position[1]
    timeBegin = datetime.now()
    print('timeBegin')
    print(timeBegin)
    print('timeEnd')
    print(timeEnd)
    writeSimulationData('epuck_circuloTrack.txt', epuck_position, epuck_orientation, jointSpeeds, None, '')
    sleep(3)

sim.stopSimulation()