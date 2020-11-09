import sim # access all the VREP elements
from time import sleep
from simulationScripts.writePositionFile import writePositionData

sim.simxFinish(-1) # just in case, close all opened connections
clientID=sim.simxStart('127.0.0.1',19999,True, True ,5000,5) # start a connection
sim.simxStartSimulation(clientID, sim.simx_opmode_oneshot)

if clientID !=-1:
   print ("Connected to remote API server")
else:
   print("Not connected to remote API server")


# handle for the left and right motors of Pioneer
err_code, left_motor_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx_leftMotor", sim.simx_opmode_blocking)
err_code, right_motor_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx_rightMotor", sim.simx_opmode_blocking)

#handle for pioneer
err_code_pioneer, pioneer_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx", sim.simx_opmode_blocking)


# start motors with 1.0 speed
err_code_left = sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 2.0, sim.simx_opmode_streaming)
err_code_right = sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 2.0, sim.simx_opmode_streaming)

# fix para contornar o "erro" na primeira leitura da posição, até que o robô inicie o movimento das rodas

positions = sim.simxGetObjectPosition(
    clientID, pioneer_handle, -1, sim.simx_opmode_streaming)

x = positions[1][0]

while x == 0:
    positions = sim.simxGetObjectPosition(
        clientID, pioneer_handle, -1, sim.simx_opmode_streaming)
    x = positions[1][0]

# Enquanto o robô anda, vai fazendo a leitura de sua posição

xInt = int(x)
while x > -3:
   positions = sim.simxGetObjectPosition(
      clientID, pioneer_handle, -1, sim.simx_opmode_buffer)
   x = positions[1][0]
   if int(x) <= xInt - 1: # Cada metro do eixo X percorrido é um checkpoint para se pegar dados da posição, odometria e sensor atuais
       xInt = int(x)
       checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(xInt + 1) + ' y: ' + str(positions[1][1])
       print(checkInfo)
       writePositionData(positions, 'pioneer_longTrack.txt', checkInfo)
       print('\n')

# Momento de rotação do robô, diminuindo a velocidade do motor referente a direção desejada
sim.simxSetJointTargetVelocity(clientID, left_motor_handle, 1, sim.simx_opmode_blocking)
sim.simxSetJointTargetVelocity(clientID, right_motor_handle, 0.5, sim.simx_opmode_blocking)

positions = sim.simxGetObjectPosition(
    clientID, pioneer_handle, -1, sim.simx_opmode_buffer)
y = positions[1][1]
sleep(17)
print('acabou tempo')

sim.simxSetJointTargetVelocity(clientID, left_motor_handle, 2, sim.simx_opmode_blocking)
sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 2, sim.simx_opmode_blocking)

yInt = int(y)
while y < 3:
    positions = sim.simxGetObjectPosition(
      clientID, pioneer_handle, -1, sim.simx_opmode_buffer)
    y = positions[1][1]
    if int(y) > yInt:
        yInt = int(y)
    #    print('Checkpoint: o robô chegou no metro x: ' + str(positions[1][0]) + ' y: ' + str(yInt))
        checkInfo = 'Checkpoint: o robô chegou no metro x: ' + str(positions[1][0]) + ' y: ' + str(yInt - 1)
        print(checkInfo)
        writePositionData(positions, 'pioneer_longTrack.txt', checkInfo)
        print('\n')

sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 1, sim.simx_opmode_blocking)
sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 0.5, sim.simx_opmode_blocking)
positions=sim.simxGetObjectPosition(
clientID, pioneer_handle, -1, sim.simx_opmode_buffer)
x = positions[1][0]
y = positions[1][1]
sleep(19)
print('acabou2')


sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 1, sim.simx_opmode_blocking)
sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 1, sim.simx_opmode_blocking)

while x < 5:
    positions = sim.simxGetObjectPosition(
        clientID, pioneer_handle, -1, sim.simx_opmode_buffer)
    x = positions[1][0]
    if int(x) > xInt:
       xInt = int(x)
       checkInfo = 'Checkpoint: o robô chegou no metro x: ' + \
           str(xInt - 1) + ' y: ' + str(positions[1][1])
       print(checkInfo)
       writePositionData(positions, 'pioneer_longTrack.txt', checkInfo)
       print('\n')

err_code_left2 = sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 0, sim.simx_opmode_blocking)
err_code_right2 = sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 0, sim.simx_opmode_blocking)

stopSim = sim.simxStopSimulation(clientID, sim.simx_opmode_blocking)
print('closed')
# print(stopSim)
