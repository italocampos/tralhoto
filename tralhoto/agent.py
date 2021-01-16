'''
Agent Module
------------

This module models the agents of the system. Here are defined the entire 
tructure of the agents and their first actions after instantiated.

@author: @italocampos
'''

from pade.core.agent import Agent

from tralhoto.board import Board
from tralhoto import config
from tralhoto.behaviour.bus import WaitBefore
from tralhoto.behaviour.station import BusListener
from tralhoto.behaviour.semaphore import BoardManager
from tralhoto.behaviour.semaphore import OpeningRequestsListener
from tralhoto.behaviour.semaphore import ConfirmationsListener
from tralhoto.behaviour.semaphore import TraditionalManager

import random, threading


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
    requests : int
        The number of non-attended opening requests for this semaphores.
    new_request : threading.Event
        An event object that sinalizes when a new request arrives for this
        Semaphore.
    MAX_OPENING_TIME : float
        The max time that this semaphore can remain open for the BRT bus
        before closes.
    MIN_CLOSING_TIME : float
        The minimum time that this semaphore must wait before open again.
    '''

    def __init__(self, aid, group, location, road, proximity_factor = 3, perimeter = None):
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

        super().__init__(aid)
        self.group = group
        self.location = location
        self.road = road
        self.proximity_factor = proximity_factor
        self.perimeter = perimeter
        self.requests = 0
        self.new_request = threading.Event()

        # Setting the opening and closing times according with the config file
        self.MAX_OPENING_TIME = config.SEMAPHORE_MAX_OPENING_TIME[group]
        self.MIN_CLOSING_TIME = config.SEMAPHORE_MIN_CLOSING_TIME[group]
    

    def setup(self):
        ''' Executes the prior actions for the agent. '''

        # Sets the locations of the proximity sensor
        self.road[self.location - self.proximity_factor][0].append({
          'aid': self.aid,
          'type': 'semaphore',
          'side': 'A',
        })
        self.road[self.location + self.proximity_factor][0].append({
          'aid': self.aid,
          'type': 'semaphore',
          'side': 'B',
        })

        # Sets the location of the Board of this semaphore
        self.road[self.location][1] = Board()

        # Initiates listener behaviours
        self.add_behaviour(BoardManager(self))
        self.add_behaviour(ConfirmationsListener(self))
        self.add_behaviour(OpeningRequestsListener(self))

        # Adds traditional behaviour
        #self.add_behaviour(TraditionalManager(self))
    

    @property
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
            gp = self.group,
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
    side : str ('A' or 'B')
        The service side of this station.
    proximity_factor : int
        The number of cells of the road vector arround the Station that define
        the area to start the communication with the buses. Default = 2.
    name : str
        The name of this Station.
    data : numpy.ndarray
        The data of passengers flow between stations and buses.
    '''

    def __init__(self, aid, group, location, road, side = None, proximity_factor = 5, name = None):
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
        side : str ('A' or 'B'), optional
            The service side of this station.
        proximity_factor : int, optional
            The number of cells of the road vector arround the Station that
            define the area to start the communication with the buses. Default
            = 2.
        name : str, optional
            The name of this Station.
        '''

        super().__init__(aid)
        self.name = name
        self.location = location
        self.group = group
        self.proximity_factor = proximity_factor
        self.road = road
        self.side = side

        # Generating discrete values to simulate the passenger movimentation
        self.data = [round(x) for x in config.scenario()]


    def setup(self):
        ''' Executes the prior actions for the agent. '''

        # Sets the locations of the proximity sensor
        self.road[self.location - self.proximity_factor][0].append({
          'aid': self.aid,
          'type': 'station',
          'side': 'A',
        })
        self.road[self.location + self.proximity_factor][0].append({
          'aid': self.aid,
          'type': 'station',
          'side': 'B',
        })

        # Adding behaviour to listen the resquests from buses
        self.add_behaviour(BusListener(self))


    def wait_time(self):
        ''' Returns the time that the bus must stay in this station.

        Returns
        -------
        float
            The amout of time that the bus must wait in this Station.
        '''

        return round(random.choice(self.data) * (1 / (1 + self.group))) * config.TIME_PER_PASSENGER


    def __str__(self):
        return '{name}\nLocation: {loc}, #{gp}'.format(
            name = self.name,
            loc = self.location,
            gp = self.group,
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
    semaphore_fifo : list
        A list that implements a FIFO behaviour to store the addresses of the
        semaphores that were messaged.
    next_station : dict
        Stores data about the next station to stop.
    n_semaphores : int
        The total number of semaphores that this bus stoped in the last trip.
    burned_stations : int
        The total number of station that this bus burned out.
    trip_time : float
        The total time (in seconds) of the trip.
    semaphore_time : float
        The time spent by this Bus in closed semaphores.
    start_time : float, optional
        The time when this bus will start to run. Default = 10.
    n_simulations : int, optional
        The number of times that this bus will trip. Default = 10
    _residual : float
        The residual value after computed the next location of this Bus.
    '''

    def __init__(self, aid, road, name = None, velocity = 45, start_time = 10, n_simulations = 10):
        '''
        aid : pade.core.aid.AID
            The AID of this agent
        name : str, optional
            The name of this Bus.
        road : list
            A list representing the road of BRT buses. The elements of the list
            must be:
                ([{'address': AID, 'type': str}], board.Board])
        velocity : float, optional
            The speed parameter for the Bus (km/h). Default = 45.
        start_time : float, optional
            The time when this bus will start to run. Default = 10.
        n_simulations : int, optional
            The number of times that this bus will trip. Default = 10
        '''
    
        super().__init__(aid)
        self.name = name
        self.velocity = velocity
        self.road = road
        self.start_time = start_time
        self.n_simulations = n_simulations
        self.location = 0
        self.side = 'A'
        self.next_station = {
            'location': None,
            'wait_time': 0,
            'name': None
        }
        self.semaphore_fifo = list()
        self.semaphore_time = 0.0
        self.trip_time = 0.0
        self.n_semaphores = 0
        self.burned_stations = 0
        self._residual = 0.0


    def setup(self):
        ''' Executes the prior actions for the agent. '''

        # Adding behaviour to move the bus
        self.add_behaviour(WaitBefore(self, self.start_time, self.n_simulations))


    def trip(self):
        ''' Calculates the number of cells in the road that this Bus will reach
        after 1 second of simulation. This value variates according with the
        velocity of this Bus.

        This method also automatically increments the trip time.

        Returns
        -------
        list
            A list with the positions to forward.
        '''

        # Converting the velocity from km/h to m/s
        ms = self.velocity / 3.6

        # Gets the number of cells to step
        n = int((self._residual + ms) / 100)
        # Updates the residual value
        self._residual = (self._residual + ms) % 100
        # Increments the total trip time
        self.trip_time += 1
        return [self.step() for _ in range(n)]
    

    def step(self):
        ''' Return the next location for the Bus.

        Returns
        -------
        int
            The position of the next location of the Bus
        '''

        if self.side == 'A':
            if self.location + 1 < len(self.road):
                self.location += 1
            else:
                self.side = 'B'
                self.location -= 1
        
        elif self.side == 'B':
            if self.location - 1 >= 0:
                self.location -= 1
            else:
                self.side = 'A'
                self.location += 1
        
        return self.location
    

    def __str__(self):
        return '{name}\n{vel} km/h #{pos} {side}'.format(
            name = self.name,
            vel = self.velocity,
            pos = self.location,
            side = '>>' if self.side == 'A' else '<<'
        )