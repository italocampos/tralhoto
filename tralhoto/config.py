'''
Config Module
-------------

This module carries the config for the simulations of the system.

@author: @italocampos
'''

''' The semaphores can be of three types, according with the degree of traffic
    in their perimeters.

    Group    Degree of traffic    
    0        High
    1        Normal
    2        Low

    Similarly, the stations can be of three types, according with their
    occupancy rate throughout the day.

    Groups  Occupancy rate
    0       High
    1       Normal
    2       Low

    Two scenarios will be used: the peak scenario and the normal scenario.
    There are two values representing the passenger flow for each bus in each
    station. This number represents the number of passengers that get or drop
    out of the bus. The standard values are defined as:

    Scenario    Flow value
    Peak        27 (3**3)
    Normal      9 (3**2)
'''

# Defines the max opening time for each semaphore group (in seconds). The
# indexes of this list maps the groups of the semaphores.
SEMAPHORE_MAX_OPENING_TIME = [30, 45, 90]

# Defines the minimum closing time for each semaphore group (in seconds). The
# indexes of this list maps the group of the semaphores.
SEMAPHORE_MIN_CLOSING_TIME = [60, 45, 30]

# Defines the flow value for the scenarios
NORMAL = 9; PEAK = 27
SCENARIO = NORMAL

# Defines the default loading and unloading time for each passenger (in seconds)
TIME_PER_PASSENGER = 2.5

# The value of the seconds in the simulation
SECONDS = 0.5