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
road = [[[], None] for _ in range(205)]

agents = list()

# Creating the Station agents
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

# Creating the Semaphore agents
for i, semaphore in enumerate(data.semaphores):
    agents.append(Semaphore(
        aid = 'semaphore-%d' % i,
        group = semaphore['group'],
        location = int(semaphore['location'] * 10) + 6,
        road = road,
        perimeter = semaphore['perimeter'],
        proximity_factor = 2,
    ))

# Creating the Bus agents
agents.extend([
    Bus(aid = 'bus-0',
        road = road,
        name = 'TB0 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[0],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 5, # Starts at simulation minute 5
    ),
    Bus(aid = 'bus-1',
        road = road,
        name = 'TB1 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[1],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 15, # Starts at simulation minute 15
    ),
    Bus(aid = 'bus-2',
        road = road,
        name = 'TB2 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[2],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 25,
    ),
    Bus(aid = 'bus-3',
        road = road,
        name = 'TB3 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[3],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 35,
    ),
    Bus(aid = 'bus-4',
        road = road,
        name = 'TB4 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[4],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 45,
    ),
    Bus(aid = 'bus-5',
        road = road,
        name = 'TB5 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[0],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 55,
    ),
    Bus(aid = 'bus-6',
        road = road,
        name = 'TB6 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[1],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 65,
    ),
    Bus(aid = 'bus-7',
        road = road,
        name = 'TB7 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[2],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 75,
    ),
    Bus(aid = 'bus-8',
        road = road,
        name = 'TB8 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[3],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 85,
    ),
    Bus(aid = 'bus-9',
        road = road,
        name = 'TB9 Maracacuera São Brás',
        velocity = config.BUS_VELOCITY[4],
        n_simulations = 10,
        start_time = config.SECOND * 60 * 95,
    ),
])

if __name__ == '__main__':
    start_loop(agents)