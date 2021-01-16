'''
Semaphore Behaviours Module
---------------------------

This module contains the behaviours of the Semaphore agents.

@author: @italocampos
'''

from pade.behaviours.types import CyclicBehaviour
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.misc.utility import display

from tralhoto import config


class BoardManager(CyclicBehaviour):
    ''' This behaviour manages the opening and closing of the board of this
    Semaphore.

    This behaviour is activated every time that the self.requests counter is
    greater than zero.
    '''

    def action(self):
        self.agent.new_request.wait()
        self.open_board()
    

    def close_board(self):
        ''' Closes the board and locks the behaviour during a minimum time, as
        is described in the config file.
        '''

        # Closes the board
        self.agent.board.close()
        # Waits for the minimum closing time
        self.wait(self.agent.MIN_CLOSING_TIME * config.SECOND)
    

    def open_board(self):
        ''' Opens the board and waits for the max opening time defined in the
        config file.
        
        If all the requests were attended before the timeout, the board is
        closed again. The same happens if the requests were not attended.
        '''

        # Opens the board
        self.agent.board.open()
        # Waits for the max opening time set in config file
        for _ in range(self.agent.MAX_OPENING_TIME):
            # Check every second if all the requests were attended
            if self.agent.requests == 0:
                break
            self.wait(config.SECOND)
        
        self.close_board()



class OpeningRequestsListener(CyclicBehaviour):
    ''' This behaviour listens for the opening requests made by the buses and
    calls the board manager ever it is necessary.
    '''

    def action(self):
        message = self.read()
        filter = Filter()
        filter.set_ontology('OPEN')
        filter.set_performative(ACLMessage.REQUEST)
        if filter.filter(message):
            if self.agent.requests == 0:
                self.agent.new_request.set()
            self.agent.requests += 1



class ConfirmationsListener(CyclicBehaviour):
    ''' This behaviour listens for the confirmations of the buses when they
    passed by the location of this semaphore.

    This behaviour also decrease the self.agent.requests variable.
    '''

    def action(self):
        message = self.read()
        filter = Filter()
        filter.set_ontology('CONFIRMATION')
        filter.set_performative(ACLMessage.INFORM)
        if filter.filter(message):
            self.agent.requests -= 1
            if self.agent.requests == 0:
                self.agent.new_request.clear()



class TraditionalManager(CyclicBehaviour):
    ''' This behaviour implements the traditional board management for the
    Semaphores (for comparison).
    '''

    def action(self):
        self.open_board()
        self.close_board()
    

    def close_board(self):
        ''' Closes the board and locks the behaviour during a minimum time, as
        is described in the config file.
        '''

        # Closes the board
        self.agent.board.close()
        # Waits for the minimum closing time
        self.wait(self.agent.MIN_CLOSING_TIME * config.SECOND)
    

    def open_board(self):
        ''' Opens the board and locks the behaviour during a minimum time, as
        is described in the config file.
        '''

        # Opens the board
        self.agent.board.open()
        # Waits the max time
        self.wait(self.agent.MAX_OPENING_TIME * config.SECOND)