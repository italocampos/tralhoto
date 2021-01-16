'''
Bus Behaviours Module
---------------------

This module contains the behaviours of the Bus agents.

@author: @italocampos
'''

from pade.behaviours.types import TickerBehaviour, OneShotBehaviour, WakeUpBehaviour
from pade.acl.messages import ACLMessage
from pade.misc.utility import display

from tralhoto.protocol import Request
from tralhoto import config

import pickle, color


class WaitBefore(WakeUpBehaviour):
    ''' Makes the bus wait a certain time before put it in run.
    
    This is used to make different buses init at different times.
    
    Properties
    ----------
    n_simulations : int
        The number of times that this bus will trip.
    '''

    def __init__(self, agent, time, n_simulations):
        '''
        Parameters
        ----------
        n_simulations : int
            The number of times that this bus will trip.
        '''

        super().__init__(agent, time * config.SECOND)
        self.n_simulations = n_simulations


    def on_wake(self):
        self.agent.add_behaviour(Run(self.agent, config.SECOND, self.n_simulations))



class Run(TickerBehaviour):
    ''' Simulates the bus running in the road.
    
    Here we define what actions the bus must take when it hits the comunication
    points with the stations and semaphores on the road.

    Properties
    ----------
    n_simulations : int
        The max number of simulations of this behaviour.
    simulation : int
        The number of the current simulation (starts with 0).
    _done : bool
        A bool that sinalizes when terminate this behaviour.
    '''

    def __init__(self, agent, time, n_simulations):
        '''
        Parameters
        ----------
        agent : tralhoto.agent.Bus
            The Bus agent that holds this behaviour.
        time : float
            The time to wait before repeat this behaviour until it ends.
        n_simulations : int
            The max number of simulations of this behaviour.
        '''

        super().__init__(agent, time)
        self.n_simulations = n_simulations
        self.simulation = 0
        self._done = False


    def on_tick(self):
        for index in self.agent.trip():
            display(self.agent, 'Triping the km %.1f.' % (index/10))

            # Checks if this is a point of stop (a station)
            if index == self.agent.next_station['location']:
                display(self.agent, color.yellow('STOP > ', 'bold') + self.agent.next_station['name'] + ' | %.1f s' % self.agent.next_station['wait_time'])
                self.agent.trip_time += self.agent.next_station['wait_time']
                self.wait(self.agent.next_station['wait_time'] * config.SECOND)

            # Send messages for any compatible agents in this point
            for address in self.agent.road[index][0]:

                # If there is a station nearby 
                if address['type'] == 'station' and address['side'] == self.agent.side:
                    # > Send a message for the nearby station
                    self.agent.add_behaviour(MessageStation(self.agent, address['aid']))

                # If there is a semaphore nearby
                elif address['type'] == 'semaphore' and address['side'] == self.agent.side:
                    # > Send a message for the nearby semaphore
                    self.agent.add_behaviour(MessageSemaphore(self.agent, address['aid']))
                    self.agent.semaphore_fifo.append(address['aid'])

            # Look at the Board of the semaphore
            board = self.agent.road[index][1]
            if board != None:
                if not board.is_opened():
                    display(self.agent, color.red('STOPED > ', 'bold') + 'Semaphore in #%d' % self.agent.location)
                    self.agent.n_semaphores += 1
                    while not board.is_opened():
                        self.agent.trip_time += 1
                        self.agent.semaphore_time += 1
                        self.wait(config.SECOND)
                self.agent.add_behaviour(ConfirmSemaphore(self.agent, self.agent.semaphore_fifo.pop(0)))
                #   QUE TAL COLOCAR O ENVIO DA CONFIRMAÇÃO EM UM OUTRO BEHAVIOUR ACIONADO
                # JUNTO COM O DE SOLICITAÇÃO DE ABERTURA. ESSE COMPORTAMENTO VAI MONITORAR A
                # POSIÇÃO DO BONDE E ENVIAR A MENSAGEM QUANDO PASSAR NA LOCALIZAÇÃO  DO SEMÁFORO (ONDE É?)
            
            # Checks if the bus finished its trip
            if self.agent.side == 'B' and self.agent.location == 0:
                display(self.agent, color.green('FINISHED > ', 'bold') + 'Trip time: %.1f s' % self.agent.trip_time)
                with open('%s.csv' % self.agent.aid.getLocalName(), 'a') as log:
                #with open('logs/buses.csv', 'a') as log:
                    log.write('{bus_name}, {velocity}, {tt}, {bs}, {sem_n}, {sem_t}\n'.format(
                        bus_name = self.agent.name,
                        velocity = self.agent.velocity,
                        tt = self.agent.trip_time,
                        bs = self.agent.burned_stations,
                        sem_n = self.agent.n_semaphores,
                        sem_t = self.agent.semaphore_time,
                        ))
                # Restart the counters
                self.agent.burned_stations = 0
                self.agent.trip_time = 0
                self.agent.n_semaphores = 0
                self.agent.semaphore_time = 0
                # Increments the simulation number
                self.simulation += 1
                if self.simulation >= self.n_simulations:
                    display(self.agent, color.magenta('SIMULATION FINISHED > ', 'bold') + 'Check the file logs/%s.csv' % self.agent.aid.getLocalName())
                    self._done = True
                else:
                    # Aguarda 10 min antes de começar a viagem novamente.
                    self.wait(10 * config.SECOND)
    

    def done(self):
        ''' Sinalizes the end of this behaviour. '''

        return self._done



class MessageStation(OneShotBehaviour):
    ''' Message the Station when inside de contact area.

    Properties
    ----------
    station : pade.core.aid.AID
        The AID of the station to be messaged.
    '''

    def __init__(self, agent, station):
        '''
        Parameters
        ----------
        agent : tralhoto.agent.Bus
            The Bus agent that holds this behaviour.
        station : pade.core.aid.AID
            The AID of the Station to be messaged.
        '''

        super().__init__(agent)
        self.station = station


    def action(self):
        # > Creates the message to send
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_ontology('HOW_MANY_TIME')
        message.set_content(pickle.dumps({'side': self.agent.side}))
        message.add_receiver(self.station)
        
        # > Calls a Request behaviour to deal with the responses
        request = Request(self.agent, message)
        self.agent.add_behaviour(request)
        # >> Waits for the Request returning
        response = self.wait_return(request)[0]
        
        # > Checks the response 
        if response.get_ontology() == 'WAIT_FOR_X_SECONDS':
            content = pickle.loads(response.get_content())
            #print(content)
            self.agent.next_station['wait_time'] = content['time']
            self.agent.next_station['location'] = content['location']
            self.agent.next_station['name'] = content['name']

            # Checks if this bus burned the location of the station
            if self.agent.side == 'A' and content['location'] <= self.agent.location:
                display(self.agent, color.red('BURNED > ', 'b') + content['name'])
                self.agent.burned_stations += 1
            elif self.agent.side == 'B' and content['location'] >= self.agent.location:
                display(self.agent, color.red('BURNED > ', 'b') + content['name'])
                self.agent.burned_stations += 1

        elif response.get_ontology() == 'INCOMPATIBLE_SIDE':
            self.agent.next_station['wait_time'] = 0 # Watis no time
            self.agent.next_station['location'] = None
            self.agent.next_station['name'] = None
        


class MessageSemaphore(OneShotBehaviour):
    ''' Message the Semaphore when inside de contact area.

    Properties
    ----------
    semaphore : pade.core.aid.AID
        The AID of the semaphore to be messaged.
    '''

    def __init__(self, agent, semaphore):
        '''
        Parameters
        ----------
        agent : tralhoto.agent.Bus
            The Bus agent that holds this behaviour.
        semaphore : pade.core.aid.AID
            The AID of the Semaphore to be messaged.
        '''

        super().__init__(agent)
        self.semaphore = semaphore


    def action(self):
        # > Creates and sends the message to send
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_ontology('OPEN')
        message.add_receiver(self.semaphore)
        self.send(message)



class ConfirmSemaphore(OneShotBehaviour):
    ''' Message a Semaphore after passed by this.

    Properties
    ----------
    semaphore : pade.core.aid.AID
        The AID of the Semaphore to be messaged.
    '''

    def __init__(self, agent, semaphore):
        '''
        Parameters
        ----------
        agent : tralhoto.agent.Bus
            The Bus agent that holds this behaviour.
        semaphore : pade.core.aid.AID
            The AID of the Semaphore to be messaged.
        '''

        super().__init__(agent)
        self.semaphore = semaphore


    def action(self):
        # > Creates and sends the message to send
        message = ACLMessage(ACLMessage.INFORM)
        message.set_ontology('CONFIRMATION')
        message.add_receiver(self.semaphore)
        self.send(message)