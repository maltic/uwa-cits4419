import dsr
from multiprocessing import Process, Pipe
import random
import time

         # x  0  1  2  3  4     y
CAN_TALK = [ [1, 0, 0, 0, 0], # 0
             [0, 1, 0, 0, 0], # 1
             [0, 0, 1, 0, 0], # 2
             [0, 0, 0, 1, 0], # 3
             [0, 0, 0, 0, 1] ]# 4
             
           # 0 = False
           # 1 = True
           
NUM_NODES = 5

COMM_LOC = 'simulator_communication/'

def _node_simulation(q, log_to, node_addr, other_nodes):
  log = open(log_to, 'a')
  dsr = dsr.DSR(q)
  
  while True:
    to = random.choice(other_nodes)
    contents = 'AAAAA'
    
    log.write('Sending ' + contents + ' to ' + str(to))
    dsr.send_message(contents, to)
    
    time.sleep(1)
    
    log.write('DSR update')
    dsr.update()
    
    time.sleep(1)
    
    frommsg = dsr.pop_messages()
    log.write('From messages; ' + frommsg)

class Simulator:
  def __init__(self, num_nodes, talk_matrix):
    assert(len(talk_matrix) == num_nodes)
  
    self.num_nodes = num_nodes
    self.talk_matrix = [ [bool(x) for x in y] for y in talk_matrix ]
    self.processes = [None] * num_nodes
    self.pipes = [None] * num_nodes
    
    for i in range(num_nodes):
      out_p, in_c = Pipe()
      in_p, out_c = Pipe()
      args = ((out_c, in_c), COMM_LOC + str(i) + '.log', i, [x for x in range(num_nodes) if x != i])
      self.processes[i] = Process(target=_node_simulation, args=args)
      self.out_pipes[i] = out_p
      self.in_pipes[i] = in_p
    
  def can_talk(self, a, b):
    return self.talk_matrix[a][b]
    
  def start(self):
    [p.start() for p in self.processes]
    
    while True:
      for i, pipe in enumerate(self.in_pipes):
        while pipe.poll():
          toaddr, msg = pipe.recv()
          if toaddr == 255:
            for j, opipe in enumerate(self.out_pipes):
              if self.can_talk(i, j):
                opipe.write((i, msg))
          else:
            if self.can_talk(i, toaddr):
              self.out_pipes[toaddr].write((i, msg))
    
Simulator(NUM_NODES, CAN_TALK)