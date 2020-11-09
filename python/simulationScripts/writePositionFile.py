def writePositionData(positions, fileName, checkpointInfo):
    file = open(fileName, 'a')
    file.write(checkpointInfo)
    file.write('\n')
    file.write('X: ' + str(positions[1][0]) + ' Y: ' + str(positions[1][1]))
    file.write('\n \n')
    file.close()

def writeSensingData(sensorData, fileName):
    file = open(fileName, 'a')
    file.write(sensorData)
    file.close()

def writeOdometryData(odomData, fileName):
    file = open(fileName, 'a')
    file.write(odomData)
    file.close()