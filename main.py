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
		name = 'Maracacuera - São Brás',
		velocity = config.BUS_VELOCITY[0],
		n_simulations = 1,
		start_time = 4,
	),
	#Bus(aid = 'bus-1',
	#	road = road,
	#	name = '801 - Testing Bus',
	#	velocity = config.BUS_VELOCITY[1],
	#	n_simulations = 1,
	#	start_time = 30,
	#),
])

if __name__ == '__main__':
	start_loop(agents)