import sys

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import writeEpuckSimData, writeEpuckSimDataOnlyDistance

def readEpuckDataImitationOnlyDistance(filename):
    filtered_checks = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    for check in checkpoints:
        if check not in filtered_checks:
            filtered_checks.append(check)

    print('checkpoints')
    print(len(checkpoints))
    print('filtered_checks')
    print(len(filtered_checks))
    i = 0
    for check in filtered_checks:
        i += 1
        wheels = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()

        # lights = splitData[0]
        sensor_clear = []
        sensors = splitData[0].split(',')
        # print('sensors', sensors)
        for sen in sensors:
            sensor_clear.append(float(sen))
        wheels = splitData[1]
        writeEpuckSimDataOnlyDistance(filename + '_filtered.txt', sensor_clear, wheels)

def readEpuckDataImitation(filename):
    filtered_checks = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    for check in checkpoints:
        if check not in filtered_checks:
            filtered_checks.append(check)

    print('checkpoints')
    print(len(checkpoints))
    print('filtered_checks')
    print(len(filtered_checks))
    i = 0
    for check in filtered_checks:
        i += 1
        wheels = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()

        lights = splitData[0]
        sensor_clear = []
        sensors = splitData[1].split(',')
        # print('sensors', sensors)
        for sen in sensors:
            sensor_clear.append(float(sen))
        wheels = splitData[2]
        writeEpuckSimData(filename + '_filtered.txt', lights, sensor_clear, wheels)

def specialFilterEpuck(filename):
    filtered_checks = []
    ultra_checks = []
    file = open(filename, 'r')
    simulation_data = file.read()
    checkpoints = simulation_data.split(';')
    checkpoints.pop() # Remove string vazia que fica após o último ';' 

    # 0.09019608050584793,0.09019608050584793,0.09019608050584793|0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05|0.4363323129985824,0.4363323129985824;
    for check in checkpoints:
        if check not in filtered_checks:
            filtered_checks.append(check)
        # light_sensor, distance_sensor, wheel_speed = check.split('|')
        # print(light_sensor)
        # print(distance_sensor)
        # print(wheel_speed)

    for filtered in filtered_checks:
        light_sensor, distance_sensor, wheel_speed = filtered.split('|')

        if distance_sensor == '0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05' and len(ultra_checks) < 10:
           ultra_checks.append(filtered)

        if filtered not in ultra_checks and distance_sensor != '0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05':
            ultra_checks.append(filtered)

    print('checkpoints')
    print(len(checkpoints))
    print('ultra_checks')
    print(len(ultra_checks))

    i = 0
    for check in ultra_checks:
        i += 1
        wheels = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()

        lights = splitData[0]
        sensor_clear = []
        sensors = splitData[1].split(',')
        # print('sensors', sensors)
        for sen in sensors:
            sensor_clear.append(float(sen))
        wheels = splitData[2]
        writeEpuckSimData(filename + '_special_filtered.txt', lights, sensor_clear, wheels)


if sys.argv[2] == '1':
    # readEpuckDataImitationOnlyDistance(sys.argv[1])
    readEpuckDataImitation(sys.argv[1])
elif sys.argv[2] == '2':
    specialFilterEpuck(sys.argv[1])