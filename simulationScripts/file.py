from itertools import count
from venv import create
import numpy as np
import os

def removeCharactersFromData(list_data):
    list_data = list_data.replace('[', '').replace(']', '').replace(' ', '')

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


def separateSensorAndAction(sensor_data):
    light_list = []
    sensor_list = []
    action_list = []
    print('ENTROU CHANGESENSOR')
    print(sensor_data)
    for i in range(len(sensor_data)):
        if i in [9, 10]: # antes era 9,10
            # print(i)
            action_list.append(sensor_data[i])
        elif i == 0:
            light_list.append(sensor_data[i])
        else:
            sensor_list.append(sensor_data[i])
    
    # print('sensor_list')
    # print(sensor_list[0])
    # print('action_list')
    # print(action_list)

    return light_list, sensor_list, action_list

def writeEpuckSimData(filename, light_data, sensor_data, wheel_data):
    createDirectories(filename)

    # print('wheel_data ANTES')
    # print(wheel_data)

    light_data = removeCharactersFromData(str(light_data))
    sensor_data = removeCharactersFromData(str(sensor_data))
    wheel_data = removeCharactersFromData(str(wheel_data))

    # print('light_data')
    # print(light_data)
    # print('sensor_data')
    # print(sensor_data)
    # print('wheel_data')
    # print(wheel_data)

    file = open(filename, 'a+')
    file.write(str(light_data) + '|')
    file.write(str(sensor_data) + '|')
    file.write(str(wheel_data) + ';')

    file.close()

    return

def writeEpuckPosition(filename, position_data):
    createDirectories(filename)

    position_data = [position_data[0], position_data[1]]
    position_data = removeCharactersFromData(str(position_data))
    file = open(filename, 'a+')
    file.write(position_data + ';')
    file.close()

def writeSimulationData(filename, position_data, orientation_data, wheel_data, sensor_data):

    createDirectories(filename)

    position_data = [position_data[0], position_data[1]]
    position_data = removeCharactersFromData(str(position_data))
    wheel_data = removeCharactersFromData(str(wheel_data))
    
    file = open(filename, 'a+')
    file.write(position_data + '|')
    
    if orientation_data:
        orientation_data = orientation_data[2]

        # if orientation_data <= -3.12 or (orientation_data > -1 and orientation_data <= -0.0): # tratamento
        #     orientation_data = -orientation_data
        orientation_data = removeCharactersFromData(str(orientation_data))
        file.write(orientation_data + '|')

    file.write(wheel_data + '|')

    if sensor_data == None:
        file.write(';')

    else:
        formatted_sensor_data = ''
        for point in sensor_data:
            dist = str(point[0])
            point_x = str(point[1])
            point_y = str(point[2])
            formatted_sensor_data = dist + ',' + point_x + ',' + point_y + '/'
            file.write(formatted_sensor_data)
        file.write(';')

    file.close()

def readEpuckDataImitation(filename):
    observations = []
    actions = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    for check in checkpoints:
        tipo = ''
        obs = []
        wheels = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()

        lights = splitData[0]
        sensors = splitData[1].split(',')
        wheels = splitData[2]

        # print('lights')
        # print(lights)

        # sensors = sensors.split(',')
        # print('sensors')
        # print(sensors)
        # print('wheels')
        # print(wheels)

        light_1 = float(lights.split(',')[0])
        light_2 = float(lights.split(',')[1])
        light_3 = float(lights.split(',')[2])
        obs.append(light_1)
        obs.append(light_2)
        obs.append(light_3)

        # print(len(sensors))
        for i in range(len(sensors)):
            sen = float(sensors[i])
            obs.append(sen)

        l_wheel_speed = float(wheels.split(',')[0])
        r_wheel_speed = float(wheels.split(',')[1])

        observations.append(obs)
        actions.append([l_wheel_speed, r_wheel_speed])

        obs = []
    
    tipo = 'withSensor'
    # print('observations')
    # print(observations)
    # print('actions')
    # print(actions)
    observations.append(observations[len(observations) - 1]) # 28 + 1 no observation

    return observations, actions, tipo
    


def readDataImitation(filename):
    observations = []
    actions = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    for check in checkpoints:
        tipo = ''
        obs = []
        jointSpeeds = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()
            # print('splitData apos pop')
            # print(splitData)
        # splitData.pop()
        position = splitData[0]
        pos_x = float(position.split(',')[0])
        pos_y = float(position.split(',')[1])
        obs.append(pos_x)
        obs.append(pos_y)

        if len(splitData) == 3: # tem orientação
            gamma_angle = float(splitData[1])
            jointSpeeds = splitData[2]
            obs.append(gamma_angle)
            tipo = 'withOrientation'

        elif len(splitData) == 4: # tem sensor
            gamma_angle = float(splitData[1])
            jointSpeeds = splitData[2]
            
            obs.append(gamma_angle)

            points = splitData[3]
            sensorData = points.split('/')
            sensorData.pop()
            # print(sensorData)
            for point in sensorData:
                pointData = point.split(',')
                for data in pointData:
                    obs.append(float(data))

            tipo = 'withSensor'
            print('FOI TIPO SENSOR PO')

        else: # sems sensor e sem orientação
            jointSpeeds = splitData[1]
            tipo = 'onlyPosicao'

        l_wheel_speed = float(jointSpeeds.split(',')[0])
        r_wheel_speed = float(jointSpeeds.split(',')[1])

        # print('ReadDataIMIT obs')
        # print(obs)
        # print([l_wheel_speed, r_wheel_speed])
        observations.append(obs)
        # observations.append([pos_x, pos_y, gamma_angle])
        actions.append([l_wheel_speed, r_wheel_speed])

        obs = [] # limpa obs para preparar para o próximo checkpoint

    observations.append(observations[len(observations) - 1]) # 28 + 1 no observation

    return observations, actions, tipo


def formatObservation(pos_x, pos_y, gamma_angle, sensorData):
    # menor_num = 0
    obs_formatted = []

    obs_formatted.append(pos_x)
    obs_formatted.append(pos_y)

    if gamma_angle:
        obs_formatted.append(gamma_angle)

    if sensorData:
        for array_points in sensorData:
            for point in array_points:
                obs_formatted.append(point)
            # if float(point) < menor_num:
            #     menor_num = float(point)

    # print('menor valor de sensor encontrado: ')
    # print(menor_num)

    return obs_formatted

def readEpuckTrainandTestPos(train_filepath, test_filepath):
    expected_positions = []
    model_positions = []

    train_file = open(train_filepath, 'r')
    test_file = open(test_filepath, 'r')
    train_data = train_file.read()
    test_data = test_file.read()

    checkpoints_train_data = train_data.split(';')
    checkpoints_test_data = test_data.split(';')
    checkpoints_train_data.pop()
    checkpoints_test_data.pop()

    print('checkpoints_train_data')
    print(len(checkpoints_train_data))
    print('checkpoints_test_data')
    print(len(checkpoints_test_data))

def readTrainAndTestPositions(train_filepath, test_filepath):
    expected_positions = []
    model_positions = []
    last_valid_pos = []

    train_file = open(train_filepath, 'r')
    test_file = open(test_filepath, 'r')
    train_data = train_file.read()
    test_data = test_file.read()

    checkpoints_train_data = train_data.split(';')
    checkpoints_test_data = test_data.split(';')
    checkpoints_train_data.pop()
    checkpoints_test_data.pop()

    for i in range(len(checkpoints_train_data)):
        split_train_data = checkpoints_train_data[i].split('|')
        # split_test_data = checkpoints_test_data[i].split('|')

        try:
            split_test_data = checkpoints_test_data[i].split('|')
        except:
            if not last_valid_pos:
                last_valid_pos = i - 1
            split_test_data = checkpoints_test_data[last_valid_pos].split('|')

        posx_train = float(split_train_data[0].split(',')[0])
        posy_train = float(split_train_data[0].split(',')[1])
        posx_test = float(split_test_data[0].split(',')[0])
        posy_test = float(split_test_data[0].split(',')[1])

        expected_positions.append([posx_train, posy_train])
        model_positions.append([posx_test ,posy_test])

    return expected_positions, model_positions


def readTrainAndTestActions(train_filepath, test_filepath):
    expected_actions = []
    predicted_actions = []
    last_valid_action = []

    train_file = open(train_filepath, 'r')
    test_file = open(test_filepath, 'r')
    train_data = train_file.read()
    test_data = test_file.read()

    checkpoints_train_data = train_data.split(';')
    checkpoints_test_data = test_data.split(';')
    checkpoints_train_data.pop()
    checkpoints_test_data.pop()

    for i in range(len(checkpoints_train_data)):
        split_train_data = checkpoints_train_data[i].split('|')

        try:
            split_test_data = checkpoints_test_data[i].split('|')
        except:
            if not last_valid_action:
                last_valid_action = i - 1
            split_test_data = checkpoints_test_data[last_valid_action].split('|')

        # print(split_train_data[2])
        # print(split_test_data)

        train_jointSpeeds = split_train_data[2]
        test_jointSpeeds = split_test_data[2]

        l_wheel_speed_train = float(train_jointSpeeds.split(',')[0])
        r_wheel_speed_train = float(train_jointSpeeds.split(',')[1])
        l_wheel_speed_test = float(test_jointSpeeds.split(',')[0])
        r_wheel_speed_test = float(test_jointSpeeds.split(',')[1])

        expected_actions.append([l_wheel_speed_train, r_wheel_speed_train])
        predicted_actions.append([l_wheel_speed_test ,r_wheel_speed_test])

    # print("Expected actions:")
    # print(expected_actions)

    # print("predicted_actions")
    # print(predicted_actions)

    return expected_actions, predicted_actions






