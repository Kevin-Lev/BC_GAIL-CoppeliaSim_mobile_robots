from datetime import datetime
from time import sleep
from zmqRemoteApi import RemoteAPIClient
from simulationScripts.file import writeSimulationData
from simulationScripts.sensorData import getSensorData

client = RemoteAPIClient('localhost',23000)

sim = client.getObject('sim') # controle da simulação
# simOMPL = client.getObject('simOMPL') # Plugin ompl para motion planning

if sim:
    print("Conectado com o Coppelia Sim!")

if sim.getSimulationState()!=sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState()!=sim.simulation_stopped:
        sleep(0.1)

loadedScene = sim.loadScene('../cenas/pioneer_longTrack.ttt')

if loadedScene != -1:
    print('Carregou cena pioneer_longTrack.ttt!')
else:
    print('falha ao tentar carregar cena!')

# Run a simulation in synchronous mode:
# client.setStepping(True)

now = datetime.now()
today_date = str(now.day) + '_' + str(now.month) + '_' + str(now.year)
fileDirectory = 'simulationData/pioneer_longTrack/pioneer_longTrack_' + today_date + '.txt'

sim.startSimulation() #Executa a simulação

print('Simulação iniciada!')

# laserHandle=sim.getObjectHandle("LaserScannerLaser_2D")
# r = sim.handleProximitySensor(laserHandle)

# print(r)

# handles iniciais
pioneer_handle = sim.getObjectHandle('Pioneer_p3dx')
left_motor_handle = sim.getObjectHandle('Pioneer_p3dx_leftMotor')
right_motor_handle = sim.getObjectHandle('Pioneer_p3dx_rightMotor')
orientation = sim.getObjectOrientation(pioneer_handle, -1)
# laserHandle= sim.getObjectHandle("LaserScannerLaser_2D")

positions = sim.getObjectPosition(pioneer_handle, -1)
pos_x = positions[0]
pos_y = positions[1]

# print('orientation')
# print(orientation)

# ativa os motores com velocidade 2.0
sim.setJointTargetVelocity(left_motor_handle, 2.0)
sim.setJointTargetVelocity(right_motor_handle, 2.0)


while pos_x == 0:
    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_x = positions[0]

xInt = int(pos_x)

# Enquanto o robô anda, vai fazendo a leitura de sua posição
while pos_x > -3:
    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_x = positions[0]
    
    # Cada metro do eixo X percorrido é um checkpoint para se pegar dados da posição, orientação e sensor atuais
    if int(pos_x) <= xInt - 1:
        xInt = int(pos_x)
        checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(xInt + 1) + ' y: ' + str(positions[1])
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
        print(checkInfo)
        sensorResult = getSensorData("pointsConverted")
        
        writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, sensorResult)
        print('\n')


# Momento de rotação do robô, diminuindo a velocidade do motor referente a direção desejada
sim.setJointTargetVelocity(left_motor_handle, 1.0)
sim.setJointTargetVelocity(right_motor_handle, 0.5)

positions = sim.getObjectPosition(pioneer_handle, -1)
orientation = sim.getObjectOrientation(pioneer_handle, -1)
y = positions[1]
# print(orientation)
gamma_angle = orientation[2]

while gamma_angle <= 0:
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    gamma_angle = orientation[2]

while gamma_angle >= 1.6:
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    gamma_angle = orientation[2]


print('acabou tempo')


sim.setJointTargetVelocity(left_motor_handle, 2.0)
sim.setJointTargetVelocity(right_motor_handle, 2.0)


yInt = int(pos_y)
while y < 3:
    positions = sim.getObjectPosition(pioneer_handle, -1)
    y = positions[1]
    if int(y) > yInt:
        yInt = int(y)
    #    print('Checkpoint: o robô chegou no metro x: ' + str(positions[1][0]) + ' y: ' + str(yInt))
        checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(positions[0]) + ' y: ' + str(yInt - 1)
        print(checkInfo)
        jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
        sensorResult = getSensorData("pointsConverted")
        writeSimulationData(fileDirectory, positions, orientation, jointsSpeed, sensorResult)
        print('\n')


sim.setJointTargetVelocity(left_motor_handle, 1.0)
sim.setJointTargetVelocity(right_motor_handle, 0.5)
positions = sim.getObjectPosition(pioneer_handle, -1)
pos_x = positions[0]
pos_y = positions[1]

while gamma_angle >= -0.0:
    orientation = sim.getObjectOrientation(pioneer_handle, -1)
    gamma_angle = orientation[2]
    # print('gamma_angle')
    # print(gamma_angle)

print('acabou2')

sim.setJointTargetVelocity(left_motor_handle, 1.0)
sim.setJointTargetVelocity(right_motor_handle, 1.0)

while pos_x < 5:
    positions = sim.getObjectPosition(pioneer_handle, -1)
    pos_x = positions[0]
    if int(pos_x) > xInt:
       xInt = int(pos_x)
       checkInfo = 'Checkpoint: o robô chegou no metro x: ' + \
           str(xInt - 1) + ' y: ' + str(positions[1])
       print(checkInfo)
       jointsSpeed = [sim.getJointTargetVelocity(left_motor_handle), sim.getJointTargetVelocity(right_motor_handle)]
       sensorResult = getSensorData("pointsConverted")
       writeSimulationData(fileDirectory, positions, orientation , jointsSpeed, sensorResult)

sim.setJointTargetVelocity(left_motor_handle, 0.0)
sim.setJointTargetVelocity(right_motor_handle, 0.0)

sim.stopSimulation()

# If you need to make sure we really stopped:
while sim.getSimulationState()!=sim.simulation_stopped:
    sleep(0.1)

sim.closeScene()

