import sys

sys.path.append('/home/kevin-lev/Área de Trabalho/Mestrado/projeto_e_anotacoes/BC_GAIL-CoppeliaSim_mobile_robots')
from simulationScripts.file import writeEpuckSimData

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

    for check in filtered_checks:
        tipo = ''
        obs = []
        wheels = []
        splitData = check.split('|')

        if splitData[len(splitData) - 1] == '':
            splitData.pop()

        lights = splitData[0]
        sensor_clear = []
        sensors = splitData[1].split(',')
        for sen in sensors:
            sensor_clear.append(float(sen))
        wheels = splitData[2]
        writeEpuckSimData(filename + '_filtered.txt', lights, sensor_clear, wheels)


readEpuckDataImitation(sys.argv[1])