from collections import deque
import math
from random import random
from copy import copy
from numpy import arange

#defining constants

L = 2000
C = 1000000.0
T = 1000


class PacketQueue:
    def __init__(self, buffer_size = None):

        #initial global variables
        self.deque = deque()
        self.buffer_size = buffer_size
        self.current_size = 0

        #counters
        self.arrivals = 0
        self.departures = 0
        self.observations = 0

        self.total_packet_counter = 0
        self.drop_packet_counter = 0

        self.idle_counter = 0
        self.initial_idle_time = 0
        self.total_idle_counter = 0

        self.total_time = 0
        self.total_size = 0
    
    def perform_des(self, question_number):
        #select simulation time -> create queue events and thier corresponding time
        #determine range of rho values depending on flag(for q3, q4 and q6)
        numbers = []

        if(question_number == 3):
            min_rho = 0.25
            max_rho = 0.95
        elif(question_number == 4):
            min_rho = 1.2
            max_rho = 1.2
        else:
            min_rho = 0.5
            max_rho = 1.5
        
        #for range of traffic density values perform DES
            
        for traffic_density in arange(min_rho, max_rho + 0.05, 0.1):

            #reset variables everytime a new traffic density is used
            self.deque = deque()
            self.current_size = 0
            self.arrivals = 0
            self.departures = 0
            self.observations = 0
            self.total_packet_counter = 0
            self.idle_counter = 0
            self.drop_packet_counter = 0
            self.total_idle_counter = 0
            self.total_size = 0
            self.total_time = 0
            self.initial_idle_time = 0

            #calculate values for lambda and alpha to populate event queues
            lda = traffic_density * C / L

            # alpha is at least 5 times lambda
            alpha = 5 * lda

            #create the arrival events
            self.create_arrival_events(lda)

            #if there is a K specified, create mm1k departure events, if not then mm1
            if self.buffer_size:
                self.create_mm1k_departures(self.deque)
            else:
                self.create_mm1_departures(self.deque)
            
            #create observers
            self.create_observers(alpha)

            #process events
            #once the events have been created, process each event

            #set size to 0 in the beginning
            self.current_size = 0

            #while there are events in the deque and total time hasn't exceeded the limit
            while self.deque and self.total_time < T:
                
                #take the event off the top of the deque (FIFO)
                event = self.deque.popleft()
                key = list(event.keys())[0]

                #set total time passed to the time of the event
                self.total_time = event.get(key)

                #if the event is an arrival event
                if key == 'a':
                    self.arrivals += 1
                    
                    #if current size exceeds buffer size, packet is dropped
                    if self.buffer_size and self.current_size >= self.buffer_size:
                        self.drop_packet_counter += 1
                    
                    else:
                        self.current_size += 1

                    #reset idle counters
                    self.total_idle_counter += self.idle_counter
                    self.idle_counter = 0
                    self.initial_idle_time = event.get(key)

                #if the event is a departure event                    
                elif key == 'd':
                    self.departures += 1
                    self.current_size -= 1

                    #reset idle counters
                    self.total_idle_counter += self.idle_counter
                    self.idle_counter = 0
                    self.initial_idle_time = event.get(key)

                #if the event is an observer event
                else:
                    self.observations += 1
                    self.total_size += self.current_size
                    
                    if self.current_size == 0:
                        #idle counter becomes current event's time - previous event's time
                        self.idle_counter = event.get(key) - self.initial_idle_time
                
            #get results
            numbers.append(self.stats(traffic_density, self.buffer_size))

        #return results as a list of lists
        return numbers
                    
    def stats(self, rho, K = None):

        #average number of packets as a string
        E_N = str(self.total_size * 1.0 / self.observations)
        
        #mm1k
        if K:

            #probability of loss is the number of packets dropped divided by the number of packets arrived
            P_LOSS = str(self.drop_packet_counter * 1.0 / self.arrivals)
            res = [str(K), "%.2f" % rho, E_N, P_LOSS]
            print(', '.join(res))

            return res

        #mm1            
        else:

            P_IDLE = str(self.total_idle_counter * 1.0 / T)
            res = ["%.2f" % rho, E_N, P_IDLE]
            print(', '.join(res))

            return res

    def create_arrival_events(self, lda):
        #create random arrival events
        current_time = 0
        arrivals = deque()

        while current_time < T:
            #random generated arrival time
            arrival_gap = -(1/lda) * math.log(1- random())
            current_time += arrival_gap
            arrivals.append({'a' : current_time})
            
        #add arrivals to the main deque
        self.merge_deques(arrivals, 'a')

    def create_mm1_departures(self, arrivals):
        #create random mm1 departure events
        current_time = 0
        departures = deque()

        #create a departure event for every arrival event
        for arrival in arrivals:

            #generate a random service time
            length = -L*math.log(1- random())
            service_time = length/C
            
            #create the departure time depending on the arrival time, service time and time of previous departure event
            #the departure time must be either more than time of previous departure or more than arrival time
            arrival_time = arrival.get('a')
            if arrival_time <= current_time:
                departure_time = current_time + service_time
            else:
                departure_time = arrival.get('a') + service_time
            
            current_time = departure_time

            departures.append({'d' : departure_time})
        
        #merge into combined deque
        self.merge_deques(departures, 'd')
    
    def create_mm1k_departures(self, arrivals):
        #now we need a packets deque to keep track of our buffer due to limited size
        #in the beginning the deque only has arrivals
        arrivals_copy = copy(arrivals)
        departures = deque()
        
        #buffer
        packets = deque()

        #total_times
        current_time = 0
        transmission_time = 0
        total_time = 0

        #while there is something in the arrivals
        while (arrivals_copy or packets) and current_time < T:

            #service the packet if possible within arrival event's time
            if packets and (not arrivals_copy or arrivals_copy[0].get('a') >= transmission_time + packets[0]):

                service_time = packets.popleft()
                
                #create the departure events
                total_time += service_time
                current_time = total_time
                transmission_time = current_time
                departures.append({'d' : current_time})

            #add arrivals to packets
            else:
                curr_event = arrivals_copy.popleft()
                key = list(curr_event.keys())[0]
                total_time = curr_event.get(key)

                if packets:
                    #decrement total time + service time from the top packet
                    packets[0] -= total_time - transmission_time
                    transmission_time += total_time - transmission_time
                
                if len(packets) < self.buffer_size:
                    #add packet if there is space in the buffer
                    service_time = (-L)*math.log(1 - random()) / C
                    packets.append(service_time)

        #merge deques
        self.merge_deques(departures, 'd')        

    def create_observers(self, alpha):
        observers = deque()
        current_time = 0

        while current_time < T:
            #generate random time
            current_time += (-1/alpha) * math.log(1-random())
            observers.append({'o' : current_time})

        #merge observers into main deque
        self.merge_deques(observers, 'o')
    
    def merge_deques (self, deque_to_merge, event_type) :
        #merge two deques together
        merged = deque()

        while self.deque and deque_to_merge:
            
            #get the key which refers to the type of the event at the top of the deque
            key = list(self.deque[0].keys())[0]
            
            #sort, take the smaller one first from both deques
            if deque_to_merge[0].get(event_type) < self.deque[0].get(key):
                merged.append(deque_to_merge.popleft())
            else:
                merged.append(self.deque.popleft())

        #if there is something in already, append    
        if self.deque:
            merged += self.deque
        
        else:
            merged += deque_to_merge
        
        #set main deque to new merged deque
        self.deque = merged
        
    















        



        










        
