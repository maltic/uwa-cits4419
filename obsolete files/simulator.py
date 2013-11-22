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
from multiprocessing import Process, Pipe, freeze_support
import random
import time
import sys
import string

               # x  0  1  2  3  4        y
CAN_TALK = [(0,  [ [0, 1, 1, 1, 1],    # 0
                   [1, 0, 1, 1, 1],    # 1
                   [1, 1, 0, 1, 1],    # 2
                   [1, 1, 1, 0, 1],    # 3
                   [1, 1, 1, 1, 0] ]), # 4

            (3,  [ [0, 1, 1, 1, 1],
                   [1, 0, 1, 1, 1],
                   [1, 1, 0, 1, 1],
                   [1, 1, 1, 0, 1],
                   [1, 1, 1, 1, 0] ]),

            (6,  [ [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0] ]),

            (9,  [ [0, 1, 1, 1, 1],
                   [1, 0, 1, 1, 1],
                   [1, 1, 0, 1, 1],
                   [1, 1, 1, 0, 1],
                   [1, 1, 1, 1, 0] ])]


           # 0 = False
           # 1 = True

NUM_NODES = 5
RUN_LOOPS = 10

COMM_LOC = 'logs/'

def _node_simulation(q, log_to, node_addr, other_nodes, loops):
  sys.stdout = open(log_to, 'a')
  sys.stderr = open(log_to+".err", 'a')
  print('SIMULATOR: Node {} online'.format(node_addr))

  d = dsr.DSR(node_addr)

  for i in range(loops):
    print('== LOOP {} =='.format(i))
    to = random.choice(other_nodes)
    contents = ''.join([random.choice(string.ascii_letters) for _ in range(6)])

    print('SIMULATOR: Sending "{}" to {}'.format(contents, to))
    d.send_message(contents, to)
     
    out_pipe = q[0] #get the output pipe
    #send everything in the nodes outbox
    for msg, addr in d.pop_outbox():
      out_pipe.send((addr,msg)) #place mesage on pipe to be send on network
      
    in_pipe = q[1]
    while in_pipe.poll():
      d.receive_packet(in_pipe.recv()[1])

    time.sleep(0.5)
    d.update()
    time.sleep(0.5)

    frommsg = d.pop_inbox()
    print('SIMULATOR: From messages; {}'.format(frommsg))
    print()

    sys.stdout.flush()
    sys.stderr.flush()

  #d.network.stop_timer()
  print('==== END ====')

class Simulator:
  def __init__(self, num_nodes, talk_matrix, loops, comm_loc):
    #assert(len(talk_matrix) == num_nodes)

    self.num_nodes = num_nodes
    #self.talk_matrix = [ [bool(x) for x in y] for y in talk_matrix ]
    self.processes = [None] * num_nodes
    self.out_pipes = [None] * num_nodes
    self.in_pipes = [None] * num_nodes
    self.comm_loc = comm_loc
    self.loops = loops
    self.start_time = 0

    for i in range(num_nodes):
      out_p, in_c = Pipe()
      in_p, out_c = Pipe()
      args = ((out_c, in_c), self.comm_loc + str(i) + '.log', i, [x for x in range(num_nodes) if x != i], loops)
      self.processes[i] = Process(target=_node_simulation, args=args)
      self.out_pipes[i] = out_p
      self.in_pipes[i] = in_p

  def can_talk(self, a, b):
    time_diff = int(time.time() - self.start_time)
    prev_m = CAN_TALK[0][1]
    for t, m in CAN_TALK:
       if time_diff > t:
          prev_m = m
       if time_diff < t:
          break

    return prev_m[a][b] == 1

  def start(self):
    print('Running simulation; will terminate automatically and gracefully after {} loops.'.format(self.loops))

    [p.start() for p in self.processes]
    self.start_time = time.time()

    while any(p.is_alive() for p in self.processes):
      for i, pipe in enumerate(self.in_pipes):
        while pipe.poll():
          toaddr, msg = pipe.recv()
          for j, opipe in enumerate(self.out_pipes):
            if self.can_talk(i, j):
              print ("is there anybody out there")
              opipe.send((i, msg))

    print('Completed. Consult logs at "{}" for more info'.format(self.comm_loc))

if __name__ == '__main__':
  freeze_support()
  s = Simulator(NUM_NODES, CAN_TALK, RUN_LOOPS, COMM_LOC)
  s.start()
