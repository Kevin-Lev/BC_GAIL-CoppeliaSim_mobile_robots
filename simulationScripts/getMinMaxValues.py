import sys
from turtle import left
sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')

def getMinMaxActionValue(file, min_left, min_right, max_left, max_right):
    # min_left, min_right, max_left, max_right = 0.0, 0.0, 2.0, 2.0 
    file = open(file, 'r')
    data = file.read()

    checkpoints_data = data.split(';')
    checkpoints_data.pop()

    for i in range(len(checkpoints_data)):
        split_data = checkpoints_data[i].split('|')

        jointSpeeds = split_data[2]
        l_wheel_speed = float(jointSpeeds.split(',')[0])
        r_wheel_speed = float(jointSpeeds.split(',')[1])

        if l_wheel_speed < min_left:
            min_left = l_wheel_speed

        if r_wheel_speed < min_right:
            min_right = r_wheel_speed

        if l_wheel_speed > max_left:
            max_left = l_wheel_speed

        if r_wheel_speed > max_right:
            max_right = r_wheel_speed

    return min_left, min_right, max_left, max_right

