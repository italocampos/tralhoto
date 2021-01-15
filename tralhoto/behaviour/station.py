'''
Station Behaviours Module
-------------------------

This module contains the behaviours of the Station agents.

@author: @italocampos
'''

from pade.behaviours.types import CyclicBehaviour
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.misc.utility import display

import pickle


class BusListener(CyclicBehaviour):
    ''' This behaviour listens for bus requests when the buses are inside the
    proximity area.
    '''

    def action(self):
        message = self.read()
        filter = Filter()
        filter.set_ontology('HOW_MANY_TIME')
        filter.set_performative(ACLMessage.REQUEST)

        if filter.filter(message):
            content = pickle.loads(message.get_content())
            reply = message.create_reply()

            if self.agent.side == None or self.agent.side == content['side']:
                reply.set_ontology('WAIT_FOR_X_SECONDS')
                reply.set_performative(ACLMessage.INFORM)
                reply.set_content(pickle.dumps({
                    'time' : self.agent.wait_time(),
                    'location' : self.agent.location,
                    'name': self.agent.name,
                }))
            else:
                reply.set_ontology('INCOMPATIBLE_SIDE')
                reply.set_performative(ACLMessage.REFUSE)
            
            self.send(reply)
            
