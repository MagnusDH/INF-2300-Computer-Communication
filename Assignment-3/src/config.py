"""Main config file used to control key aspects of a particular simulation run.
"""
# Tips: Make it work for one thing at a time:
# - Start with dropped packets only
# - Then corrupted packets only
# - Then delayed packets only

# Keep the number of packets low in the beginning

# Number of packets per simulation
PACKET_NUM = 6

# The size of each packet in bytes.
# The data in each packet will be uppercase ASCII letters only!
PACKET_SIZE = 1

# The seed ensures a new run is identical to the last
RANDOM_SEED = 84737869  # I love you! :)
# If you don't want an identical run, set this to True
RANDOM_RUN = False

# The chance that each packet is dropped
DROP_CHANCE = 0.25
# The chance that the data in a packet is changed
CORRUPT_CHANCE = 0.0

# The chance that the packet is delayed
DELAY_CHANCE = 0.5
# Delay in seconds
DELAY_AMOUNT = 0.5



#MY VARIABLES

#Number of packet that can be sent at a time
WINDOW_SIZE = 5
ALL_PACKETS_DELIVERED = 0   #0 = NO, 1 = YES
TEST = 0
ALICE_EXPECTS_ACK = -1
ALICE_NUM_SENDT = 0
ALICE_NUM_RECEIVED = 0
ALICE_LAST_ACKNOWLEDGED_PACKET = -1
BOB_LAST_ACKNOWLEDGED_PACKET = 0
BOB_EXPECT_PACKET = 0
BOB_NUM_RECEIVED = 0









        #ALice: Receive packet from application layer
        #Alice: mark packet with ID
        

        #If window can still be filled up
            #Place packet in window[packet.id]
            #If: this is the first package ever sent
                #start timer
                #Send packet

            #Else: This is not the first package that is sent
                #If: alice has received acknowledgement for last sent package
                    #If: base == nextseqnum
                        #start timer                    
                    #Send packet
                
                #Else: Alice has not received acknowledgement for last sent packet
                    #Wait for timer to go out and re-send all packets in current window

        #!!!!!!!!!!!!!!!!!START WORKING FROM HERE!!!!!!!!!!!!!!!!!!!!!!!
        #Else: window is full and no more packages can be sent
            #???????
            #Buffer packet
            #If (Alice_last_ack > window[packet.id % WINDOW_SIZE])
                #send packet that is in buffer  
        #!!!!!!!!!!!!!!!!!!!!!THIS FUNCTION NEEDS TO BE SOLVED!!!!!!!!!!!!!!!





        #Bob is the receiver of a packet
            #If: packet has correct sequence number
                #Place packet.data in application layer
                #Acknowledge packet and send it to Alice

            #Else: packet has wrong sequence number
                #Send last acknowledged packet number to Alice
                        




        #Alice is the receiver of this packet
            #If: packet has correct sequence number
                #Increment pointer to lowest package pointer

                #If we have acknowledgement for the last packet, then quit program
                    #Cancel timer
                
                #Else: this is not the last package
                    #Increment package number that Alice expects

            #Else: packet has wrong sequence number 
                #Re-send all packets in current window