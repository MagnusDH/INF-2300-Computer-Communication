from copy import copy
from threading import Timer
from packet import Packet

from config import *
import time
import config

class TransportLayer:
    """The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """

    def __init__(self):
        self.timer = None
        self.timeout = 5.0  # Seconds
        
        #MY VARIABLES
        self.window = []                                        #List containing the current packets that has been sent
        self.base = 0                                           #Lowest package number that has been sent and NOT acknowledged
        self.nextseqnum = 0                                     #Current package number that CAN be sent
        self.current_packet_id = 0                              #ID for a packet
        self.bob_last_acknowledged_packet = None                #Last packet number that Bob acknowledged
        self.bob_expect_packet = 0                              #Current packet number that Bob expects to receive
        self.alice_expect_ack = 0                               #Current packet number that Alice expects acknowledgement for
        self.bob_num_recieved = 0                               #Number of packets that Bob has received
        self.alice_num_received = 0                             #Number of acknowledgements that Alice has received

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def timer_timeout(self):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TIMER_TIMEOUT() !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("             Alice, has not recieved any acknowledgement message for package[",self.alice_expect_ack,"]")
        #Reset the timer and re-send all packet in current window
        self.reset_timer(self.timer_timeout)
        for pckt in self.window:
            pckt.receiver = 0
            pckt.acknowledged = False
            print("             Alice, re-sending packet[",pckt.id,"]")
            self.network_layer.send(pckt)


    def from_app(self, binary_data):
        """
        -Alice is using this function to recieve a packet from application layer
        """
        print("FROM_APP()")
        #Receive packet from application layer
        packet = Packet(binary_data)
        print("             Alice has received packet:", packet.data," from application layer")

        # Implement me!

        #If window can still be filled up
        if(self.nextseqnum < self.base + WINDOW_SIZE):
            #Mark packet with ID
            packet.id = self.current_packet_id
            self.current_packet_id += 1
            if self.current_packet_id >= WINDOW_SIZE:
                self.current_packet_id = 0

            #Place packet in window[packet.id]
            print("             Alice, placing packet id:[",packet.id,"] in window[",packet.id,"]")
            if(len(self.window) == WINDOW_SIZE):
                self.window[packet.id] = packet
            else:
                self.window.insert(packet.id, packet)

            #When first message is sent
            if(self.base == self.nextseqnum):
                #start timer
                print("             Alice, started timer")
                self.reset_timer(self.timer_timeout)
            
            #Send packet
            print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
            self.nextseqnum += 1
            self.network_layer.send(self.window[packet.id])

        
        #If window is full and no more packages can be sent
        else:
            print("             Alice, sending window is full, waiting for timer to expire...")


    """
        -Intervall for sent and acknowledged packets:                           [0 - base-1]      
        -Intervall for sent but not acknowledged packets:                       [base - nxt_packet-1]
        -intervall for packets that can be sent, but has not:                   [nxt_packet - base+N-1]
        -Intervall for packets that can not be sent until space is available:   [packet >= base+N]
        

        # if the window is not full, Send data
        if(nextseqnum < base + N){                          #nextseqnum < window_size basicly
            place packet number: nextseqnum, into array
            send packet from array[nextseqnum]

            #When the first message have been sent
            if(base == nextseqnum){
                start timer
            }

            nextseqnum += 1
        }
        #If the window is full and can not get more packages
        else{                                           #nextseqnum > base+N
            refuse packet, do not send until ack from
            wait for ack

            if(ack received for base packet number/expected packet number){
                increment base number += 1
                if(base == nextseqnum){
                    stop timer
                }
                else{
                    start timer
                }
            }

            #if ack received for other packet number than expected
            else{
                reset timer
                resend all packets in window
            }
        }
    """



    """
        ALICE SEND:
        -Receive packet from application layer
        
        -if: space in window AND bob has received:
            -Put package in window
    
            -if first package:
                -start timer
            
            -send package
            -increment nextseqnum
        
        -else: window is full:
            -Do not send next package
            -store message in new list
            -wait for available space in window


        ALICE RECEIVE:
        -If received ack package:
            -increment base with 1
            -If base is same number as last sent package number (means we are at the end)
                -Stop timer
            -If base is less than sent package number
                -Free up space in window
                -Fill space in window with new package
                -start timer
                -send package
        
        -Else: time out
            -restart time
            -Re-send all packets in window

        

        BOB RECEIVE:
        -receive packet from Alice
        -if packet is expected packet number:
            -deliver package to application layer
            -Send ack back to Alice
        -if packet is NOT expected package number:  (meaning package number is higher than expected)
            -if(package number is higher than expected)
                -Send last acknowledged package number to ALice

            -else(package number is lower than expected)
                -discard any packages recieved that is higher than this number
                -expected = 2, but recieved = 0
                -crop bob.data by doing:
                    -bob.data = RCTUKQ
                    -bob.data[:len(bob.data)-expected*PACKET_SIZE]
                -Send last acknowledged package number to Alice
    """

    # self.network_layer.send(packet)

    def from_network(self, packet):
        print("FROM_NETWORK()")
        
        #Bob is the receiver of this packet
        if packet.receiver == 0:
            print("             Bob, recieved from Alice: packet[",packet.id,"]: ",packet.data)

            #DONE: Packet has correct sequence number
            if(packet.id == self.bob_expect_packet):
                print("             Bob, received correct sequence number")
                self.bob_expect_packet += 1
                if(self.bob_expect_packet >= WINDOW_SIZE):
                    self.bob_expect_packet = 0
                
                #Place packet.data in application layer
                if(self.bob_num_recieved < PACKET_NUM):
                    print("             Bob, packet delivered to application layer")
                    self.application_layer.receive_from_transport(packet.data)
                    self.bob_num_recieved += 1

                #Acknowledge packet and send it to Alice
                packet.acknowledged = True
                packet.receiver = 1
                #send packet
                print("             Bob, sends acknowledgement message to Alice for packet[",packet.id,"]")
                self.bob_last_acknowledged_packet = packet.id
                self.network_layer.send(packet)

            #Packet has wrong sequence number
            else:
                print("             Bob, received wrong packet number... Sending last acknowledged packet to Alice")
                #Send last acknowledged packet number to Alice
                packet.receiver = 1
                packet.acknowledged = True
                packet.id = self.bob_last_acknowledged_packet
                self.network_layer.send(packet)
                
                # #Packet number is higher than expected
                # if(packet.id > self.bob_expect_packet):
                #     print("             Bob, received packet number that is too big... Sending last acknowledged packet to Alice")
                #     packet.receiver = 1
                #     packet.id = self.bob_last_acknowledged_packet
                #     self.network_layer.send(packet)
                # #Packet number is lower than expected
                # else:
                #     print("             Bob, received packet number that is too low... slicing bob.data and sending last acknowledged packet to Alice")
                #     # self.bob.received[:len(self.bob.received - self.bob_expect_packet*PACKET_SIZE)]       #Crop bob->data
                #     packet.receiver = 1
                #     packet.id = self.bob_last_acknowledged_packet
                #     self.network_layer.send(packet)

        
        #Alice is the receiver of this packet
        else:
            #If packet has correct sequence number
            if(packet.id == self.alice_expect_ack):
                print("             Alice has recieved acknowledgement for packet[",packet.id,"]")
                
                #Increment pointer to lowest package pointer
                self.base += 1

                #If we have acknowledgement for the last packet, then quit program
                if(self.base == PACKET_NUM):
                    print("             Alice, received acknowledgment for the last message. Quit!")
                    config.ALL_PACKETS_DELIVERED = 1
                    #Cancel timer
                    self.timer.cancel()
                
                #This is not the last package
                else:
                    #Increment package number that Alice expects, and wrap around if it is too great
                    self.alice_expect_ack += 1
                    if(self.alice_expect_ack >= WINDOW_SIZE):
                        self.alice_expect_ack = 0

            #Packet has wrong sequence number 
            else:
                print("             Alice, received acknowledgement for wrong packet number. Received: packet[",packet.id,"]")
                #Reset timer and re-send all packets in window
                self.reset_timer(self.timer_timeout)
                # for pckt in self.window:
                #     pckt.receiver = 0
                #     pckt.acknowledged = False
                #     print("             Alice, re-sending packet[",pckt.id,"]")
                #     self.network_layer.send(pckt)
        

    def reset_timer(self, callback, *args):
        """
        -If there is a timer
            -if timer is alive
                -Stop timer
        -If there is not a timer
            -Create timer
            -start timer
        """
        # This is a safety-wrapper around the Timer-objects, which are
        # separate threads. If we have a timer-object already,
        # stop it before making a new one so we don't flood
        # the system with threads!
        if self.timer:
            if self.timer.is_alive():
                self.timer.cancel()
        # callback(a function) is called with *args as arguments
        # after self.timeout seconds.
        self.timer = Timer(self.timeout, callback, *args)
        self.timer.start()













































# from copy import copy
# from threading import Timer
# from packet import Packet

# from config import *
# import time
# import config

# class TransportLayer:
#     """The transport layer receives chunks of data from the application layer
#     and must make sure it arrives on the other side unchanged and in order.
#     """

#     def __init__(self):
#         self.timer = None
#         self.timeout = 10.0  # Seconds
        
#         #MY VARIABLES
#         self.window = []                                        #List containing the current packets that has been sent
#         self.base = 0                                           #Lowest package number that has been sent and NOT acknowledged
#         self.nextseqnum = 0                                     #Current package number that CAN be sent
#         self.current_packet_id = 0                              #ID for a packet
#         self.bob_last_acknowledged_packet = None                #Last packet number that Bob acknowledged
#         self.bob_expect_packet = 0                              #Current packet number that Bob expects to receive
#         self.alice_expect_ack = -1                              #Current packet number that Alice expects acknowledgement for
#         self.bob_num_recieved = 0                               #Number of packets that Bob has received
#         self.alice_num_received = 0                             #Number of acknowledgements that Alice has received
#         self.alice_num_sent = 0                                 #Number of packets that Alice has sent
#         self.packet_buffer = [] * WINDOW_SIZE

#     def with_logger(self, logger):
#         self.logger = logger
#         return self

#     def register_above(self, layer):
#         self.application_layer = layer

#     def register_below(self, layer):
#         self.network_layer = layer

#     def timer_timeout(self):
#         print("!!!!!!!!!!!!!!!!!!!! TIMER_TIMEOUT() !!!!!!!!!!!!!!!!!!!!")
#         print("             Alice, has not recieved any acknowledgement message for package[",config.ALICE_EXPECTS_ACK,"]")
#         #Reset the timer and re-send all packet in current window
#         self.reset_timer(self.timer_timeout)
#         for pckt in self.window:
#             pckt.receiver = 0
#             pckt.acknowledged = False
#             print("             Alice, re-sending packet[",pckt.id,"]")
#             self.network_layer.send(pckt)


#     def from_app(self, binary_data):
#         """
#         -Alice is using this function to recieve a packet from application layer
#         """
#         print("FROM_APP()")
#         #Receive packet from application layer
#         packet = Packet(binary_data)
#         print("             Alice has received packet:", packet.data," from application layer")

#         # Implement me!

#         #Mark packet with ID
#         packet.id = self.current_packet_id
#         self.current_packet_id += 1
        
#         #If window can still be filled up
#         if(self.nextseqnum < self.base + WINDOW_SIZE):
#             #If this is the first package ever sent
#             if(config.ALICE_NUM_SENDT == 0):
#                 #Place packet in window[packet.id]
#                 print("             Alice, placing packet id:[",packet.id,"] in window[",packet.id % WINDOW_SIZE,"]")
#                 if(len(self.window) == WINDOW_SIZE):
#                     self.window[packet.id % WINDOW_SIZE] = packet
#                 else:
#                     self.window.insert(packet.id % WINDOW_SIZE, packet)
#                 for x in self.window:               #REMOVE THIS LATER
#                     print("             Window[",x.id % WINDOW_SIZE,"]:",  x.data)
                
#                 #This is the first message ever sendt
#                 #start timer
#                 print("             Alice, started timer")
#                 self.reset_timer(self.timer_timeout)
                
#                 #Send packet
#                 print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
#                 self.nextseqnum += 1
#                 config.ALICE_NUM_SENDT += 1
#                 config.ALICE_EXPECTS_ACK = packet.id
#                 self.network_layer.send(self.window[packet.id % WINDOW_SIZE])
            
#             #This is not the first packet that Alice sends
#             else:
#                 #Alice has received acknowledgement for the last sent packet
#                 print("!!!!!!!!!!!! PACKET ID:", packet.id, "ALICE LAST ACK PACKET:", config.ALICE_LAST_ACKNOWLEDGED_PACKET)
#                 # if(config.ALICE_EXPECTS_ACK == packet.id - 1):
#                 if(config.ALICE_LAST_ACKNOWLEDGED_PACKET == packet.id - 1):

#                     #The window still has space for other packets
#                     if(len(self.window) < WINDOW_SIZE):
#                         #Place packet in window 
#                         print("             Alice, placing packet id:[",packet.id,"] in window[",packet.id % WINDOW_SIZE,"]")
#                         if(len(self.window) == WINDOW_SIZE):
#                             self.window[packet.id % WINDOW_SIZE] = packet
#                         else:
#                             self.window.insert(packet.id % WINDOW_SIZE, packet)
#                         for x in self.window:               #REMOVE THIS LATER
#                             print("             Window[",x.id % WINDOW_SIZE,"]:",  x.data)

#                         #When first message is sent
#                         if(self.base == self.nextseqnum):
#                             #start timer
#                             print("             Alice, started timer")
#                             self.reset_timer(self.timer_timeout)
                    
#                         #Send packet
#                         print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
#                         self.nextseqnum += 1
#                         config.ALICE_NUM_SENDT += 1
#                         config.ALICE_EXPECTS_ACK = packet.id
#                         self.network_layer.send(self.window[packet.id % WINDOW_SIZE])


#                     #The window is full and the packet must replace another
#                     else:    
#                         print("             Alice, the window is full....Replacing a packet")
#                         #Find the package that was last acknowledged and replace it
#                         for pckt in self.window:
#                             if(pckt.id <= (config.ALICE_LAST_ACKNOWLEDGED_PACKET)):# - WINDOW_SIZE + 1)):
#                                 print("             Alice, replaced packet[",pckt.id,"]")
#                                 pckt = packet

#                                 #When first message is sent
#                                 if(self.base == self.nextseqnum):
#                                     #start timer
#                                     print("             Alice, started timer")
#                                     self.reset_timer(self.timer_timeout)
                    
#                                 #Send packet
#                                 print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
#                                 self.nextseqnum += 1
#                                 config.ALICE_NUM_SENDT += 1
#                                 config.ALICE_EXPECTS_ACK = packet.id
#                                 self.network_layer.send(pckt)
#                                 break
                
#                 #Alice has NOT received acknowledgement for the last sent packet
#                 else:   
#                     print("             Alice has not received acknowledgement for packet[",config.ALICE_EXPECTS_ACK,"]")
                    
#                     #Place packet in window Check if packet can be placed in window
                    
                    
#                     #The window still has space for other packets
#                     if(len(self.window) < WINDOW_SIZE):
#                         #Place packet in window 
#                         print("             Alice, placing packet id:[",packet.id,"] in window[",packet.id % WINDOW_SIZE,"]")
#                         if(len(self.window) == WINDOW_SIZE):
#                             self.window[packet.id % WINDOW_SIZE] = packet
#                         else:
#                             self.window.insert(packet.id % WINDOW_SIZE, packet)
#                         for x in self.window:               #REMOVE THIS LATER
#                             print("             Window[",x.id % WINDOW_SIZE,"]:",  x.data)

#                         # #When first message is sent
#                         # if(self.base == self.nextseqnum):
#                         #     #start timer
#                         #     print("             Alice, started timer")
#                         #     self.reset_timer(self.timer_timeout)
                    
#                         # #Send packet
#                         # print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
#                         # self.nextseqnum += 1
#                         # config.ALICE_NUM_SENDT += 1
#                         # config.ALICE_EXPECTS_ACK = packet.id
#                         # self.network_layer.send(self.window[packet.id % WINDOW_SIZE])


#                     #The window is full and the packet must replace another
#                     else:    
#                         print("             Alice, the window is full....Replacing a packet")
#                         #Find the package that was last acknowledged and replace it
#                         for pckt in self.window:
#                             if(pckt.id <= (config.ALICE_LAST_ACKNOWLEDGED_PACKET)):# - WINDOW_SIZE + 1)):
#                                 print("             Alice, replaced packet[",pckt.id,"]")
#                                 pckt = packet
#                                 break

#                                 # #When first message is sent
#                                 # if(self.base == self.nextseqnum):
#                                 #     #start timer
#                                 #     print("             Alice, started timer")
#                                 #     self.reset_timer(self.timer_timeout)
                    
#                                 # #Send packet
#                                 # print("             Alice, sending packet[",packet.id,"]:",packet.data," to Bob")
#                                 # self.nextseqnum += 1
#                                 # config.ALICE_NUM_SENDT += 1
#                                 # config.ALICE_EXPECTS_ACK = packet.id
#                                 # self.network_layer.send(pckt)
#                                 # break
                    
                    
#                     #Re-send all packages in current window
#                     self.reset_timer(self.timer_timeout)
#                     # for pckt in self.window:
#                     #     print("             Alice, re-sending packet[",pckt.id,"]")
#                     #     pckt.receiver = 0
#                     #     pckt.acknowledged = False
#                     #     self.network_layer.send(pckt)
#                     #Re-send the packet that Alice wants acknowledgement for
#                     for pckt in self.window:
#                         if(pckt.id == config.ALICE_EXPECTS_ACK):
#                             pckt.receiver = 0
#                             pckt.acknowledged = False
#                             print("             Alice, re-sending packet[",pckt.id,"]")
#                             config.ALICE_EXPECTS_ACK = pckt.id
#                             self.network_layer.send(pckt)
              
#         #If window is full and no more packages can be sent
#         else:
#             print("             Alice, WINDOW IS FULL, waiting for timer to pass!!!!!")


#     """
#         -Intervall for sent and acknowledged packets:                           [0 - base-1]      
#         -Intervall for sent but not acknowledged packets:                       [base - nxt_packet-1]
#         -intervall for packets that can be sent, but has not:                   [nxt_packet - base+N-1]
#         -Intervall for packets that can not be sent until space is available:   [packet >= base+N]
        

#         # if the window is not full, Send data
#         if(nextseqnum < base + N){                          #nextseqnum < window_size basicly
#             place packet number: nextseqnum, into array
#             send packet from array[nextseqnum]

#             #When the first message have been sent
#             if(base == nextseqnum){
#                 start timer
#             }

#             nextseqnum += 1
#         }
#         #If the window is full and can not get more packages
#         else{                                           #nextseqnum > base+N
#             refuse packet, do not send until ack from
#             wait for ack

#             if(ack received for base packet number/expected packet number){
#                 increment base number += 1
#                 if(base == nextseqnum){
#                     stop timer
#                 }
#                 else{
#                     start timer
#                 }
#             }

#             #if ack received for other packet number than expected
#             else{
#                 reset timer
#                 resend all packets in window
#             }
#         }
#     """



#     """
#         ALICE SEND:
#         -Receive packet from application layer
        
#         -if: space in window AND bob has received:
#             -Put package in window
    
#             -if first package:
#                 -start timer
            
#             -send package
#             -increment nextseqnum
        
#         -else: window is full:
#             -Do not send next package
#             -store message in new list
#             -wait for available space in window


#         ALICE RECEIVE:
#         -If received ack package:
#             -increment base with 1
#             -If base is same number as last sent package number (means we are at the end)
#                 -Stop timer
#             -If base is less than sent package number
#                 -Free up space in window
#                 -Fill space in window with new package
#                 -start timer
#                 -send package
        
#         -Else: time out
#             -restart time
#             -Re-send all packets in window

        

#         BOB RECEIVE:
#         -receive packet from Alice
#         -if packet is expected packet number:
#             -deliver package to application layer
#             -Send ack back to Alice
#         -if packet is NOT expected package number:  (meaning package number is higher than expected)
#             -if(package number is higher than expected)
#                 -Send last acknowledged package number to ALice

#             -else(package number is lower than expected)
#                 -discard any packages recieved that is higher than this number
#                 -expected = 2, but recieved = 0
#                 -crop bob.data by doing:
#                     -bob.data = RCTUKQ
#                     -bob.data[:len(bob.data)-expected*PACKET_SIZE]
#                 -Send last acknowledged package number to Alice
#     """

#     # self.network_layer.send(packet)

#     def from_network(self, packet):
#         print("FROM_NETWORK()")
#         print("Alice expects ack for package[",config.ALICE_EXPECTS_ACK,"]")
#         print("Bob expects package[",config.BOB_EXPECT_PACKET,"]")
#         print("Bob last acknowledged package[",config.BOB_LAST_ACKNOWLEDGED_PACKET,"]")

#         # Implement me!
        
#         #Bob is the receiver of this packet
#         if packet.receiver == 0:
#             print("             Bob, recieved from Alice: packet[",packet.id,"]: ",packet.data)

#             #Packet has correct sequence number
#             if(packet.id == config.BOB_EXPECT_PACKET):
#                 print("             Bob, received correct sequence number")
 
#                 #Bob can still receive packets and Alice has received ack for last package
#                 if(config.BOB_NUM_RECEIVED <= PACKET_NUM):
#                     #Alice has received acknowledgement for last packet
#                     print("ALICE EXPECT ACK:", config.ALICE_EXPECTS_ACK, "Packet delivered to Bob:",packet.id)
#                     if(config.ALICE_EXPECTS_ACK == packet.id):# config.BOB_LAST_ACKNOWLEDGED_PACKET):
#                         print("             Bob, packet delivered to application layer")
#                         self.application_layer.receive_from_transport(packet.data)
#                         config.BOB_EXPECT_PACKET += 1
#                         if(config.BOB_EXPECT_PACKET >= PACKET_NUM):
#                             config.BOB_EXPECT_PACKET = None
#                         config.BOB_NUM_RECEIVED += 1

#                         #Acknowledge packet and send it to Alice
#                         packet.acknowledged = True
#                         packet.receiver = 1
#                         #send packet
#                         config.BOB_LAST_ACKNOWLEDGED_PACKET = packet.id
#                         print("             Bob, sends acknowledgement message to Alice for packet[",config.BOB_LAST_ACKNOWLEDGED_PACKET,"]")
#                         self.network_layer.send(packet)

#                     #Alice has not received acknowledgement for last packet
#                     else:
#                         print("             Bob received correct package number, but Alice has not received correct ack message....")
#                         #Re-send last acknowledged packet to Alice
#                         packet.acknowledged = True
#                         packet.receiver = 1
#                         config.BOB_LAST_ACKNOWLEDGED_PACKET = packet.id
#                         print("             Bob, re-sends acknowledgement to Alice for packet[",config.BOB_LAST_ACKNOWLEDGED_PACKET,"]")

#                         self.network_layer.send(packet)
#                 else:
#                     print("             Bob, HAS RECEIVED ALL PACKETS!!!!!!!!!!!!")

#             #Packet has wrong sequence number
#             else:
#                 print("             Bob, received wrong packet number...")
#                 #Send last acknowledged packet number to Alice
#                 packet.receiver = 1
#                 packet.acknowledged = True
#                 packet.id = config.BOB_LAST_ACKNOWLEDGED_PACKET
#                 print("             Bob, sending last acknowledged packet[",config.BOB_LAST_ACKNOWLEDGED_PACKET,"] to Alice")
#                 self.network_layer.send(packet)
                        
#         #Alice is the receiver of this packet
#         else:
#             print("             Alice, has received packet[",packet.id,"] from Bob")
#             #If packet has correct sequence number
#             if(packet.id == config.ALICE_EXPECTS_ACK):
#                 print("             Alice has recieved acknowledgement for packet[",packet.id,"]")
#                 config.ALICE_LAST_ACKNOWLEDGED_PACKET = packet.id
#                 print("             Alice, last acknowledged_packet =", config.ALICE_LAST_ACKNOWLEDGED_PACKET)

#                 #Increment pointer to lowest package pointer
#                 self.base += 1
#                 print("BASE!!!!!! =", self.base)

#                 #If we have acknowledgement for the last packet, then quit program
#                 if(self.base >= PACKET_NUM):
#                     print("             Alice, received ack for last message!! QUIT!!!!!!!!!!!!!!!!!!!!")
#                     config.ALL_PACKETS_DELIVERED = 1
#                     #Cancel timer
#                     self.timer.cancel()
                
#             #Packet has wrong sequence number
#             else:
#                 print("             Alice, received acknowledgement for wrong packet number. Received: packet[",packet.id,"]")
#                 for pckt in self.window:
#                     pckt.receiver = 0
#                     pckt.acknowledged = False
#                     print("             Alice, re-send packet[",pckt.id,"]")
#                     self.network_layer.send(pckt)

#     def reset_timer(self, callback, *args):
#         """
#         -If there is a timer
#             -if timer is alive
#                 -Stop timer
#         -If there is not a timer
#             -Create timer
#             -start timer
#         """
#         # This is a safety-wrapper around the Timer-objects, which are
#         # separate threads. If we have a timer-object already,
#         # stop it before making a new one so we don't flood
#         # the system with threads!
#         if self.timer:
#             if self.timer.is_alive():
#                 self.timer.cancel()
#         # callback(a function) is called with *args as arguments
#         # after self.timeout seconds.
#         self.timer = Timer(self.timeout, callback, *args)
#         self.timer.start()