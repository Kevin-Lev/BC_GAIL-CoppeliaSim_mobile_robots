from zmqRemoteApi import RemoteAPIClient


def getSensorData(stringSignal_name):
    client = RemoteAPIClient('localhost',23000)
    sim = client.getObject('sim') # controle da simulação

    points_sensor = sim.getStringSignal(stringSignal_name)
    points_sensor = sim.unpackTable(points_sensor)
    
    return points_sensor

