from itertools import count
from venv import create
import numpy as np
import os

def removeCharactersFromData(list_data):
    list_data = list_data.replace('[', '').replace(']', '').replace(' ', '')
    # for data in list_data:
    #     print(data)
    #     data.replace('[', '').replace(']', '').replace(' ', '')

    return list_data

def createDirectories(directoryString):
    directories = directoryString.split('/')
    dirPath = ''

    for dir in directories:
        if '.txt' in dir:
            break

        dirPath += dir + '/'
        if os.path.exists(dirPath) == False:
            print("Criando o diretório " + dirPath)
            os.mkdir(dirPath)


def writeSimulationData(filename, position_data, orientation_data, wheel_data):

    createDirectories(filename)

    position_data = [position_data[0], position_data[1]]
    orientation_data = orientation_data[2]

    position_data = removeCharactersFromData(str(position_data))
    orientation_data = removeCharactersFromData(str(orientation_data))
    wheel_data = removeCharactersFromData(str(wheel_data))
    sensor_data = None

    

    # sensor_data = removeCharactersFromData(str(sensor_data))
    # position_data = removeCharactersFromData(position_data)

    print('position_data REMOVIDO')
    print(position_data)

    file = open(filename, 'a+')
    file.write(position_data + '|')
    file.write(orientation_data + '|')
    file.write(wheel_data + '|')
    file.write(';')
    if sensor_data:
        formatted_sensor_data = ''
        for point in sensor_data:
            dist = str(point[0])
            point_x = str(point[1])
            point_y = str(point[2])
            point_z = str(point[3])
            formatted_sensor_data = dist + ',' + point_x + ',' + point_y + ',' + point_z + '/'
            file.write(formatted_sensor_data)
        file.write(';')
            # formatted_sensor_data = dist + ',' + point_x + ',' + point_y + ',' + point_z + '/'
            # file.write(str(formatted_sensor_data) + ';')
        # file.write('(' + str(sensor_data[1]) + ', ' + str(sensor_data[2]) + ')')
    # file.write('\n')
    file.close()


def readDataImitation(filename):
    formattedCheckpoints = []
    observations = []
    actions = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    for check in checkpoints:
        splitData = check.split('|')
        # print('splitData')
        # print(splitData)
        position = splitData[0]
        pos_x = float(position.split(',')[0])
        pos_y = float(position.split(',')[1])
        gamma_angle = float(splitData[1])
        jointSpeeds = splitData[2]
        l_wheel_speed = float(jointSpeeds.split(',')[0])
        r_wheel_speed = float(jointSpeeds.split(',')[1])
        observations.append([pos_x, pos_y, gamma_angle])
        actions.append([l_wheel_speed, r_wheel_speed])

    # print('observations')
    # print(observations)
    # print('actions')
    # print(actions)

    return observations, actions
        # print('position')
        # print(position)
    # print('checkpoints')
    # print(checkpoints)


def readSimulationData(filename):
    formattedCheckpoints = []
    formattedSensor = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 
    for check in checkpoints:
        splitData = check.split('|')
        positions = np.fromstring(splitData[0], dtype=float, count=2, sep=",")
        orientation = np.fromstring(splitData[1], dtype=float, count=1, sep=",")
        wheel = np.fromstring(splitData[2], dtype=float, count=2, sep=",")
        # sensor = splitData[3]
        # # print(positions)
        # # print(orientation)
        # # print(wheel)
        # # print('sensor')
        # # print(sensor)
        # sensor_points_split = sensor.split('/')
        # sensor_points_split.pop()
        # # print(sensor_points_split)
        # for point_split in sensor_points_split:
        #     point_array = np.fromstring(point_split, dtype=float, count=4, sep=",")
        #     formattedSensor.append(point_array)
        formattedCheckpoints.append([positions, orientation, wheel])
        # formattedCheckpoints.append([positions, orientation, wheel, formattedSensor])
        # print('formattedCheckpoints')
        # print(formattedCheckpoints)
        # break
        formattedSensor = []
    print('formattedCheckpoints')
    print(formattedCheckpoints)