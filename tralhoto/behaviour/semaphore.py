'''
Semaphore Behaviours Module
---------------------------

This module contains the behaviours of the Semaphore agents.

@author: @italocampos
'''

from pade.behaviours.types import CyclicBehaviour, OneShotBehaviour
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.misc.utility import display

from tralhoto import config

import color


class RequestsSniffer(OneShotBehaviour):
    ''' Sniffs for requests don't attended by this Semaphore.

    This behaviour is called by BoardManager behaviour when there is no
    requests to attend. When some request appears, this behaviour returns back
    the control to BoardManager.
    '''

    def action(self):
        if self.agent.requests != 0:
            self.set_return(None)



class BoardManager(CyclicBehaviour):
    ''' This behaviour manages the opening and closing of the board of this
    Semaphore.

    This behaviour calls for a RequestsSniffer behaviour when there is no
    requests to attend. This behaviour get back the control when the
    RequestsSniffer detect a new request.
    '''

    def action(self):
        sniffer = RequestsSniffer(self.agent)
        self.agent.add_behaviour(sniffer)
        self.wait_return(sniffer)
        self.open_board()
    

    def close_board(self):
        ''' Closes the board and locks the behaviour during a minimum time, as
        is described in the config file.
        '''

        # Closes the board
        self.agent.board.close()
        # Waits for the minimum closing time
        self.wait(config.SEMAPHORE_MIN_CLOSING_TIME[self.agent.group] * config.SECONDS)
    

    def open_board(self):
        ''' Opens the board and waits for the max opening time defined in the
        config file.
        
        If all the requests were attended before the timeout, the board is
        closed again. The same happens if the requests were not attended.
        '''

        # Opens the board
        self.agent.board.open()
        # Waits for the max opening time set in config file
        for _ in range(config.SEMAPHORE_MAX_OPENING_TIME):
            # Check every second if all the requests were attended
            if self.agent.requests == 0:
                break
            self.wait(config.SECONDS)
        
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