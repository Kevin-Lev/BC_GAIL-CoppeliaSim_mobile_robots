# Make sure to have the add-on "Connectivity/ZMQ remote API server"
# running in CoppeliaSim
#
# Following are required and should be installed:
# pip install pyzmq
# pip install cbor

# import zm

import time
from zmqRemoteApi import RemoteAPIClient

client = RemoteAPIClient('localhost',23000)

sim = client.getObject('sim')

print('sim')
print(sim)

# Create a few dummies and set their positions:
handles = [sim.createDummy(0.01, 12 * [0]) for _ in range(50)]
for i, h in enumerate(handles):
    sim.setObjectPosition(h, -1, [0.01 * i, 0.01 * i, 0.01 * i])

# Run a simulation in asynchronous mode:
sim.startSimulation()
while (t := sim.getSimulationTime()) < 3:
    s=f'Simulation time: {t:.2f} [s] (simulation running asynchronously to client)'
    print(s)
    sim.addLog(sim.verbosity_scriptinfos,s)
sim.stopSimulation()
# If you need to make sure we really stopped:
while sim.getSimulationState()!=sim.simulation_stopped:
    time.sleep(0.1)

# Run a simulation in synchronous mode:
client.setStepping(True)
# client.setsynchronous(True)
sim.startSimulation()
while (t := sim.getSimulationTime()) < 3:
    print(f'Simulation time: {t:.2f} [s] (synchronous simulation)')
    sim.addLog(sim.verbosity_scriptinfos,f'Simulation time: {t:.2f} [s] (synchronous simulation)')
    client.step() # triggers next simulation step
sim.stopSimulation()

# Remove the dummies created earlier:
for h in handles:
    sim.removeObject(h)