'''
Main Module
-----------

This module initiates the system. Here the agents are instantiated and the
simulation data are passed to the agents.

@author: @italocampos
'''

from tralhoto.agent import Bus, Station, Semaphore
from tralhoto import config
from pade.misc.utility import start_loop
import data


# Creating the road vector
road = [([], None) for _ in range(205)]

agents = list()

# Creating Station agents
for i, station in enumerate(data.stations):
	agents.append(Station(
		aid = 'station-%d' % i,
		group = station['group'],
		location = int(station['location'] * 10) + 6,
		road = road,
		side = station['side'],
		name = station['name'],
		proximity_factor = 5
		))

# Creating Bus agents
agents.extend([
	Bus(aid = 'bus-0',
		road = road,
		name = '000 Maracacuera São Brás',
		velocity = config.BUS_VELOCITY[0],
		n_simulations = 5,
		start_time = 10,
	),
	Bus(aid = 'bus-1',
		road = road,
		name = '001 Maracacuera São Brás',
		velocity = config.BUS_VELOCITY[1],
		n_simulations = 5,
		start_time = 5 *60, # Starts 5 min after bus-0
	),
])

if __name__ == '__main__':
	start_loop(agents)