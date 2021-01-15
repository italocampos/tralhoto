'''
Config Module
-------------

This module carries the config for the simulations of the system.

@author: @italocampos
'''

import scipy.stats as stats


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
    There are two Probability Distribution Functions (PDFs) to model the data
    of passenger flow for each bus in each station. These PDFs have limiar
    values according to each scenario. In other words, these functions
    represent the number of passengers that get in or get off in each bus. The
    limiar values and the PDF for each scenario are described below:

    Scenario    Flow value      PDF
    Peak        27 (3**3)       Gaussian
    Normal      9 (3**2)        Uniform
'''

''' Below we define the funtions to generate the flow values in the stations
according with the problem modeling.
'''

def normal():
    return stats.uniform.rvs(size = 50, loc = 9, scale = 2)

def peak():
    return stats.norm.rvs(size = 50, loc = 27, scale = 2)


# Defines the max opening time for each semaphore group (in seconds). The
# indexes of this list maps the groups of the semaphores.
SEMAPHORE_MAX_OPENING_TIME = [30, 45, 90]

# Defines the minimum closing time for each semaphore group (in seconds). The
# indexes of this list maps the group of the semaphores.
SEMAPHORE_MIN_CLOSING_TIME = [60, 45, 30]

# Defines the type of scenario in the simulation
scenario = normal

# Defines the default loading and unloading time for each passenger (in seconds)
TIME_PER_PASSENGER = 3.0

# The value of the seconds in the simulation
SECONDS = 0.01

# Defining the speeds of the buses (std 35, 40)
BUS_VELOCITY = [50, 45]