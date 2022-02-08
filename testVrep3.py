import sim  # access all the VREP elements
import sys
import math
import time

def getPositionOnPath(clientID, path_handle, pos_on_path):
    emptyBuff = bytearray()

    res, retInts, retFloats, retStrings, retBuffer = sim.simxCallScriptFunction(
    clientID, 'Vehicle', sim.sim_scripttype_childscript, 'positionOnPath', [], [path_handle, pos_on_path], ['Hello world!'], emptyBuff, sim.simx_opmode_oneshot_wait)
    if res == sim.simx_return_ok:
        print(retStrings[0])

        return retFloats
    else:
        print('PositionOnPath Remote function call failed')


def matrixOperations(path_pos):
    emptyBuff = bytearray()

    res, retInts, retFloats, retStrings, retBuffer = sim.simxCallScriptFunction(
        clientID, 'Vehicle', sim.sim_scripttype_childscript, 'matrixOperations', [], path_pos, ['Hello world!'], emptyBuff, sim.simx_opmode_oneshot_wait)
    if res == sim.simx_return_ok:
        print(retStrings)

        return retFloats
    else:
        print('matrixOperations Remote function call failed')



sim.simxFinish(-1)  # just in case, close all opened connections

clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # start a connection
sim.simxSynchronous(clientID, True)

if clientID != -1:
    print("Connected to remote API server")

else:
    print("Not connected to remote API server")
    sys.exit("Could not connect")


#handle for robot
err_code_vehicle, robot_handle = sim.simxGetObjectHandle(
    clientID, "Vehicle", sim.simx_opmode_blocking)

#handle for path
err_code_vehicle, path_handle = sim.simxGetObjectHandle(
    clientID, "Path", sim.simx_opmode_blocking)


# handle for the left and right motors of vehicle
err_code, left_motor_handle = sim.simxGetObjectHandle(
    clientID, "left_motor", sim.simx_opmode_blocking)
err_code, right_motor_handle = sim.simxGetObjectHandle(
    clientID, "right_motor", sim.simx_opmode_blocking)

#initial speed to 0
err_code_left = sim.simxSetJointTargetVelocity(
    clientID, left_motor_handle, 0.0, sim.simx_opmode_streaming)
err_code_right = sim.simxSetJointTargetVelocity(
    clientID, right_motor_handle, 0.0, sim.simx_opmode_streaming)


#handle for dummy
err_code_start, start_dummy_handle = sim.simxGetObjectHandle(clientID, 'Start', sim.simx_opmode_blocking)

pos_on_path = 0
dis = 0
v_des = 0.0
om_des = 0.0

# varia entre diferentes modelos de robôs
d = 0.06 # wheels separation 
r_w = 0.0275 # wheels separation
iter = 0


while True:
    # sim.simxSetJointTargetVelocity(
    #     clientID, right_motor_handle, 0.0, sim.simx_opmode_streaming)
    # sim.simxSetJointTargetVelocity(
    #     clientID, left_motor_handle, 0.0, sim.simx_opmode_streaming)

    print("Iteration: " + str(iter))
    rob_pos = sim.simxGetObjectPosition(clientID, robot_handle, -1, sim.simx_opmode_blocking)
    path_pos = getPositionOnPath(clientID, path_handle, pos_on_path)

    # print('path_pos for dummy')
    # print(path_pos)

    sim.simxSetObjectPosition(clientID, start_dummy_handle, -1, path_pos, sim.simx_opmode_blocking)

    path_pos = matrixOperations(path_pos)

    dis = math.sqrt((path_pos[1]) ** 2 + (path_pos[2]) ** 2 )
    phi = math.atan2(path_pos[2], path_pos[1])

    # print('path_pos dps da matrix')
    # print(path_pos)

    print('dis')
    print(dis)
    print('phi')
    print(phi)

    if pos_on_path < 1:
        v_des = 0.1
        om_des = 0.8 * phi
    else:
        v_des = 0  #stop condition
        om_des = 0
        break

    v_r = (v_des + d * om_des)
    v_l = (v_des - d * om_des)

    omega_right = v_r / r_w
    omega_left = v_l / r_w

    print('omega_left')
    print(omega_left)
    print('omega_right')
    print(omega_right)

    sim.simxSetJointTargetVelocity(clientID, right_motor_handle, -omega_right, sim.simx_opmode_streaming)
    sim.simxSetJointTargetVelocity(clientID, left_motor_handle, -omega_left, sim.simx_opmode_streaming)

    if dis < 0.1:
        pos_on_path = pos_on_path + 0.01

    iter += 1

    # time.sleep(0.5)
