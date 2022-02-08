import sim  # access all the VREP elements
import time

sim.simxFinish(-1)  # just in case, close all opened connections
clientID = sim.simxStart('127.0.0.1', 19999, True, True,
                         5000, 5)  # start a connection
sim.simxStartSimulation(clientID, sim.simx_opmode_oneshot)

if clientID != -1:
   print("Conectado ao servidor remote API do Coppelia Sim")
else:
   print("Não foi possível realizar a conexão com o remote API")

# handle for the left and right motors of Pioneer
err_code, left_motor_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx_leftMotor", sim.simx_opmode_blocking)
err_code, right_motor_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx_rightMotor", sim.simx_opmode_blocking)

#handle for pioneer
err_code_pioneer, pioneer_handle = sim.simxGetObjectHandle(
    clientID, "Pioneer_p3dx", sim.simx_opmode_blocking)
# err_code_sensor, sensor_handle = sim.simxGetObjectHandle(
#     clientID, "Proximity_sensor", sim.simx_opmode_blocking)
# print('sensor')
# print(err_code_sensor)

print("Left Motor handle:" + str(left_motor_handle))
print("Error code: " + str(err_code))
print("Right Motor handle: " + str(right_motor_handle))

# start motors with 1.0 speed
count = 0
err_code_left = sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 1.0, sim.simx_opmode_streaming)
err_code_right = sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 1.0, sim.simx_opmode_streaming)


print('err_code_left')
print(err_code_left)
print('err_code_right')
print(err_code_right)

positions = sim.simxGetObjectPosition(
    clientID, pioneer_handle, -1, sim.simx_opmode_streaming)

x = positions[1][0]
print('positions')
print(positions)
print('x')
print(x)
# time.sleep(20)
# while count < 25:
#    print(count)
#    positions = sim.simxGetObjectPosition(
#       clientID, pioneer_handle, -1, sim.simx_opmode_streaming)
#    print(positions)
#    sensorReadings = sim.simxReadProximitySensor(clientID, sensor_handle, sim.simx_opmode_streaming)
#    print('sensorReadings')
#    print(sensorReadings)
#    count += 1
#    time.sleep(5)

while x < 6:
   print(count)
   positions = sim.simxGetObjectPosition(
       clientID, pioneer_handle, -1, sim.simx_opmode_streaming)
#    print(positions)
#    sensorReadings = sim.simxReadProximitySensor(clientID, sensor_handle, sim.simx_opmode_streaming)
#    print('sensorReadings')
#    print(sensorReadings)
   x = positions[1][0]
   print(x)
#    time.sleep(5)


err_code_left2 = sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 0, sim.simx_opmode_blocking)
err_code_right2 = sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 0, sim.simx_opmode_blocking)

stopSim = sim.simxStopSimulation(clientID, sim.simx_opmode_blocking) 

# print(err_code_left2)
# print(err_code_right2)

# Terminar a simulação
# pauseSim = sim.simxPauseSimulation(clientID, sim.simx_opmode_blocking)
# print(pauseSim)

# print("err_code_left: " + str(err_code_left))
# print("err_code_right: " + str(err_code_right))
# print("code_left: " + str(code_left))
# print("code_right: " + str(code_right))
