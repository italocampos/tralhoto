'''
Board Module
------------

This module contains a class modeling the board of the semaphores. This board
can be in three states, represented by colors: RED, AMBER and GREEN.

@author: @italocampos
'''

from pade.misc.thread import SharedResource
from tralhoto import config
import time


class Board(object):
    ''' The Board class.

    The Board class can have only three different colors: RED, AMBER or GREEN.

    Properties
    ----------
    _color : SharedResource
        The current color of the semaphore. Use the methods read() and write()
        to handle this object.
    _security_time : float
        The waiting time (in seconds) before the color of the Board becomes
        RED.
    '''

    def __init__(self, color = 'RED', security_time = 5.0):
        '''
        Parameters
        ----------
        color : str, optional
            The color to set in the semaphore. Default = 'RED'.
        security_time : float, optional
            The waiting time (in seconds) before the color of the Board becomes
            RED. Default = 6.0
        '''
        self._color = SharedResource('RED')
        self._security_time = security_time
        self.color = color
    

    @property
    def color(self):
        ''' Returns the current Board color.
        
        Returns
        -------
        str
            The current color of the Board.
        '''

        return self._color.read()
    

    @color.setter
    def color(self, color):
        ''' Sets a new color to Board.
        
        Parameters
        ----------
        color : str
            The color to be set in this Board.
        
        Raises
        ------
        ValueError
            When a wrong color is passed to this function.
        '''

        if color not in ['RED', 'AMBER', 'GREEN']:
            raise(ValueError('The color %s is not allowed to Board objects.' % color))
        self._color.write(color)


    def is_opened(self):
        ''' Returns a bool that indicates if this Board is green.

        Returns
        -------
        bool
            Indicates if the Board is green.
        '''

        return self.color == 'GREEN'
    

    def open(self):
        ''' Sets the color of the Board to GREEN. '''

        self.color = 'GREEN'
    

    def close(self):
        ''' Sets the color of the Board to AMBER, waits the security time, and
        finally puts the color of the Board to RED. '''

        self.color = 'AMBER'
        time.sleep(self._security_time * config.SECONDS)
        self.color = 'RED'