'''
Protocol Module
---------------

This module contains behaviours that implements simple protocols for the agents
of the system.

@author: @italocampos
'''

from pade.behaviours.types import SimpleBehaviour
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
#from pade.misc.utility import display


class Request(SimpleBehaviour):
    ''' This behaviour models a protocol of the type request-response.

    This behaviour can be used to send a request and wait for the responses.
    The required parameter is the message to be sent. The filter used to filter
    the responses is optional.

    Attributes
    ----------
    message : ACLMessage
        The message to be sent.
    filter : pade.acl.filter.Filter
        The filter used to filter the received responses.
    requested : bool
        The bool that sinalizes if the requests are sent.
    _done : bool
        The bool that sinalizes when the behaviour ends.
    requests : int
        The counter of the requests that were sent.
    '''

    def __init__(self, agent, message, filter = None):
        '''
        Parameters
        ----------
        agent : Agent
            The agent that holds thhi behaviour.
        message : ACLMessage
            The message to be sent.
        filter : pade.acl.filter.Filter, optional
            The filter used to filter the received responses.
        '''

        super().__init__(agent)
        self.message = message
        self.requested = False
        self._done = False
        self.requests = len(message.receivers)
        self.data = list()

        # If no filter was provided, use a default filter
        if filter == None:
            filter = Filter()
            filter.set_conversation_id(message.get_conversation_id())
        self.filter = filter


    def action(self):
        if not self.requested:
            self.send(self.message)
            self.requested = True
        response = self.read()
        if self.filter.filter(response):
            self.data.append(response.clone())
            self.requests -= 1
        if self.requests == 0:
            self.set_return(self.data)
            self._done = True


    def done(self):
        return self._done