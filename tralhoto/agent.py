'''
Agent Module
------------

This module models the agents of the system. Here are defined the entire 
tructure of the agents and their first actions after instantiated.

@author: @italocampos
'''

from pade.acl.aid import AID
from pade.core.agent import Agent
from pade.misc.utility import display
from pade.misc.thread import SharedResource

from tralhoto.board import Board
import tralhoto.config as config

import color, random, scipy


class Semaphore(Agent):
    ''' The class that models the agent Semaphore.

    The semaphores can be of three types, according with the degree of traffic
    in their perimeters.

    Group    Degree of traffic
    0        High
    1        Normal
    2        Low

    Properties
    ----------
    group : int
        An int that describes the group of this semaphore.
    location : int
        The location if this semaphore in the global road.
    road : list
        A list representing the road of BRT buses. The elements of the list
        must be:
            ([{'address': AID, 'type': str}], board.Board])
    proximity_factor : int
        The number of cells of the road vector arround the Semaphore that
        define the area to start the communication with the buses. Default = 2.
    perimeter : str
        Describes the perimeter correspondent to this semaphore.
    MAX_OPENING_TIME : float
        The max time that this semaphore can remain open for the BRT bus
        before closes.
    MIN_CLOSING_TIME : float
        The minimum time that this semaphore must wait before open again.
    '''

    def __init__(self, aid, group, location, road, proximity_factor = 2, perimeter = None):
        '''
        Parameters
        ----------
        aid : pade.core.aid.AID
            The AID of this agent
        group : int
            An int that describes the group of this semaphore.
        location : int
            The location if this semaphore in the road.
        road : list
            A list representing the road of BRT buses. The elements of the list
            must be:
                ([{'address': AID, 'type': str}], board.Board])
        proximity_factor : int, optional
            The number of cells of the road vector arround the Semaphore that
            define the area to start the communication with the buses. Default = 2.
        perimeter : str, optional
            Describes the perimeter correspondent to this semaphore.
        '''

        super().__init(aid)
        self.group = group
        self.location = location
        self.road = road
        self.proximity_factor = proximity_factor
        self.perimeter = perimeter

        # Setting the opening and closing times according with the config file
        self.MAX_OPENING_TIME = config.SEMAPHORE_MAX_OPENING_TIME[group]
        self.MIN_CLOSING_TIME = config.SEMAPHORE_MIN_CLOSING_TIME[group]
    

    def setup(self):
        ''' Executes the prior actions for the agent. '''

        # Sets the locations of the proximity sensor
        self.road[self.location - self.proximity_factor][0].append({
          'address': self.aid,
          'type': 'semaphore'
        })
        self.road[self.location + self.proximity_factor][0].append({
          'address': self.aid,
          'type': 'semaphore'
        })

        # Sets the location of the Board of this semaphore
        self.road[self.location][1] = Board()
    

    def board(self):
        ''' A shortcut to access the Board of this Semaphore.

        Returns
        -------
        Board
            The loacation of the read with the local Board.
        '''

        return self.road[self.location][1]
    

    def __str__(self):
        return '{per}\nLocation: {loc}, #{gp}'.format(
            per = self.perimeter,
            loc = self.location,
            gp = self.group
        )



class Station(Agent):
    ''' The class that models the agent Station.

    The station can be of three types, according with their lotation degree.

    Group    Lotation
    0        High
    1        Normal
    2        Low

    Properties
    ----------
    group : int
        An int that describes the group of this Station.
    location : int
        The location if this Station in the global road.
    road : list
        A list representing the road of BRT buses. The elements of the list
        must be:
            ([{'address': AID, 'type': str}], board.Board])
    proximity_factor : int
        The number of cells of the road vector arround the Station that define
        the area to start the communication with the buses. Default = 2.
    name : str
        The name of this Station.
    data : numpy.ndarray
        The data of passengers flow between stations and buses.
    '''

    def __init__(self, aid, group, location, road, proximity_factor = 2, name = None):
        '''
        aid : pade.core.aid.AID
            The AID of this agent
        group : int
            An int that describes the group of this Station.
        location : float
            The location if this Station in the global road.
        road : list
            A list representing the road of BRT buses. The elements of the list
            must be:
                ([{'address': AID, 'type': str}], board.Board])
        proximity_factor : int, optional
            The number of cells of the road vector arround the Station that
            define the area to start the communication with the buses. Default
            = 2.
        name : str, optional
            The name of this Station.
        '''

        super().__init(aid)
        self.name = name
        self.location = location
        self.group = group
        self.proximity_factor = proximity_factor
        self.road = road

        # Generating the values to simulate the passenger movimentation
        self.data = scipy.stats.norm.rvs(size = 50, loc = config.SCENARIO, scale = 1)


    def setup(self):
        ''' Executes the prior actions for the agent. '''

        # Sets the locations of the proximity sensor
        self.road[self.location - self.proximity_factor][0].append({
          'address': self.aid,
          'type': 'station'
        })
        self.road[self.location + self.proximity_factor][0].append({
          'address': self.aid,
          'type': 'station'
        })


    def wait_time(self):
        ''' Returns the time that the bus must stay in this station.

        Returns
        -------
        float
            The amout of time that the bus must wait in this Station.
        '''

        return random.choice(self.data) * config.TIME_PER_PASSENGER * (1 / 1 + self.group)


    def __str__(self):
        return '{name}\nLocation: {loc}, #{gp}'.format(
            name = self.name
            loc = self.location,
            gp = self.group
        )



class Bus(Agent):
    ''' The class that models the agent Bus.

    Properties
    ----------
    road : list
        A list representing the road of BRT buses. The elements of the list
        must be:
            ([{'address': AID, 'type': str}], board.Board])
    name : str
        The name of this Bus.
    velocity : float
        The speed parameter for the Bus (km/h). Default = 45.
    location : int
        The location if this Station in the global road.
    side : str ('A' or 'B')
        The current side of the road that this Bus is traveling.
    last_station : AID
        Stores the last station visited by this bus.
    _residual : float
        The residual value after computed the next location of this Bus.
    '''

    def __init__(self, aid, road, name = None, velocity = 45):
        '''
        aid : pade.core.aid.AID
            The AID of this agent
        road : list
            A list representing the road of BRT buses. The elements of the list
            must be:
                ([{'address': AID, 'type': str}], board.Board])
        name : str, optional
            The name of this Bus.
        velocity : float, optional
            The speed parameter for the Bus (km/h). Default = 45.
        '''
    
        super().__init__(aid)
        self.name = name
        self.velocity = velocity
        self.road = road
        self.location = 0
        self.side = 'A'
        #self.last_station = None
        self._residual = 0


    def setup(self):
        ''' Executes the prior actions for the agent. '''

        pass


    def trip(self):
        ''' Calculates the number of cells in the road that this Bus will reach
        after 1 second of simulation. This value variates according with the
        velocity of this Bus.

        Returns
        -------
        list
            A list with the positions to forward.
        '''

        # Gets the number of cells to step
        n = int((self._residual + self.velocity) / 100)
        # Updates the residual value
        self._residual = (self._residual + self.velocity) % 100
        return [self.next_step() for _ in range(n)]
    

    def next_step(self):
        ''' Return the next location for the Bus

        Returns
        -------
        int
            The position of the next location of the Bus
        '''

        if self.side == 'A':
            if self.location + 1 < len(self.road):
                return self.location + 1
            else:
                self.side = 'B'
                return self.location - 1
        
        if self.side == 'B':
            if self.location - 1 >= 0:
                return self.location - 1
            else:
                self.side = 'A'
                return self.location + 1
    

    def __str__(self):
        return '{name}\n{vel} km/h #{pos} {side}'.format(
            name = self.name,
            vel = self.velocity,
            pos = self.location,
            side = '>>' if self.side == 'A' else '<<'
        )