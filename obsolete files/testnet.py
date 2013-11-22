#==================================README=======================================
#
#This is a DSR protocol implementation using Python.
#
#It is the project for CITS4419 - Mobile and Wireless Computing
#at The University of Western Australia.
#
#<AUTHOR> = Ash Tyndall, Asra Alshabib, Bo Chuen Chung, Dayang Abang Mordian,
#           Hui Li Leow, Max Ward, Raphael Byrne, Timothy Raphael,
#           Vincent Sun, Zhiqiang (Cody) Qiu
#
#<SUPERVISOR> = Prof. Amitava Datta
#
#<ORGANIZATION> = The University of Western Australia
#
#<YEAR> = 2013
#
#<VERSION> = V1.0
#
#===============================================================================

#=================================BSD LICENSE===================================
#
#Copyright (c) <YEAR>, <AUTHOR>
#
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  - Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#===============================================================================

import dsr
import random
import string
import sys

SIMULATION_STEPS = 100
               # x  0  1  2  3  4        y
CAN_TALK = [(0,  [ [0, 1, 1, 1, 1],    # 0
                   [1, 0, 1, 1, 1],    # 1
                   [1, 1, 0, 1, 1],    # 2
                   [1, 1, 1, 0, 1],    # 3
                   [1, 1, 1, 1, 0] ]), # 4
                   #note that the first matrix must always be at time 0

            (3,  [ [0, 1, 1, 1, 1],
                   [1, 0, 1, 1, 1],
                   [1, 1, 0, 1, 1],
                   [0, 0, 1, 0, 1],
                   [0, 0, 1, 1, 0] ]),

            (8,  [ [0, 1, 0, 0, 0],
                   [1, 0, 1, 0, 0],
                   [0, 1, 0, 1, 0],
                   [0, 0, 1, 0, 1],
                   [0, 0, 0, 1, 0] ]),


            (SIMULATION_STEPS+1,  #this should never be reached!
                 [ [0, 1, 1, 1, 1],
                   [1, 0, 1, 1, 1],
                   [1, 1, 0, 1, 1],
                   [1, 1, 1, 0, 1],
                   [1, 1, 1, 1, 0] ])]


           # 0 = False
           # 1 = True

NODE_LIST = []


#generates a random string
def random_string():
  return ''.join([random.choice(string.ascii_letters) for _ in range(6)])



#A simulation wrapped for a DSR Node
#Handles the simulated application and network layers
class Node:
  def __init__(self, id):
    self.id = id
    self.dsr = dsr.DSR(id)
  def update(self, curr_matrix):
    #update the dsr object
    self.dsr.update()
    #get all the incoming/outgoing messages
    received = self.dsr.pop_inbox()
    toSend = self.dsr.pop_outbox()
    #display all the messages received by the application layer
    for r in received:
      print (" ------APPLICATION------ Received packet for node #"+str(self.id)+" : {}".format(r))
    #broadcast all messages on the network required by dsr
    can_talk_list = curr_matrix[self.id]
    for ts in toSend: #for every message to send
      for n in range(0, len(can_talk_list)): #for all nodes
        if can_talk_list[n] == 1: #send if connected in the network
          NODE_LIST[n].dsr.receive_packet(ts[0])


if __name__ == '__main__':
  #Whoever added the stupid log file bullshit: you can just pipe to a log file (python testnet.py > logfile)
  #init node list
  for i in range(0, len(CAN_TALK[0][1])):
    NODE_LIST.append(Node(i))
  #setup initial connectivity matrix
  curr_matrix = CAN_TALK[0][1]
  curr_index = 0
  for i in range(1,SIMULATION_STEPS):
    #a random message is sent
    fromN = random.randrange(len(NODE_LIST))
    toN = random.randrange(len(NODE_LIST))
    while (toN == fromN):
        toN = random.randrange(len(NODE_LIST))
    msg = random_string()
    print(" ------SIMULATOR-----  "+str(fromN)+" sends '"+msg+"' to "+str(toN))
    NODE_LIST[fromN].dsr.send_message(msg, toN)
    #switch to the next can talk matrix, if the current
    #iteration step matches the next network change
    if CAN_TALK[curr_index+1][0] == i:
      print(" ------SIMULATOR-----  Swapping matrix")
      curr_matrix = CAN_TALK[curr_index+1][1]
      curr_index += 1
    print("STARTING SIMULATION STEP #"+str(i))
    #step through all nodes and updare them
    for n in NODE_LIST:
      print("===================Node #"+str(n.id)+"====================")
      n.update(curr_matrix)
      print("--------------------------------------------")
      print(" ")





