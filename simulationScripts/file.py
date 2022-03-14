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


def writeSimulationData(filename, position_data, orientation_data, wheel_data, sensor_data):

    createDirectories(filename)

    position_data = [position_data[0], position_data[1]]
    position_data = removeCharactersFromData(str(position_data))
    wheel_data = removeCharactersFromData(str(wheel_data))
    
    file = open(filename, 'a+')
    file.write(position_data + '|')
    
    if orientation_data:
        orientation_data = orientation_data[2]
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



