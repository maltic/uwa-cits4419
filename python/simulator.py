import dsr
from multiprocessing import Process, Pipe, freeze_support
import random
import time
import sys
import string

         # x  0  1  2  3  4     y
CAN_TALK = [ [1, 0, 0, 0, 0], # 0
             [0, 1, 0, 0, 0], # 1
             [0, 0, 1, 0, 0], # 2
             [0, 0, 0, 1, 0], # 3
             [0, 0, 0, 0, 1] ]# 4
             
           # 0 = False
           # 1 = True
           
NUM_NODES = 5

COMM_LOC = 'logs/'

def _node_simulation(q, log_to, node_addr, other_nodes):
  sys.stdout = open(log_to, 'a')
  print('SIMULATOR: Node {} online'.format(node_addr))
  
  d = dsr.DSR(q)
  
  while True:
    to = random.choice(other_nodes)
    contents = ''.join([random.choice(string.ascii_letters) for _ in range(6)])

    print('SIMULATOR: Sending "{}" to {}'.format(contents, to))
    d.send_message(contents, to)
    
    time.sleep(0.5)
    d.update()
    time.sleep(0.5)
    
    frommsg = d.pop_messages()
    print('SIMULATOR: From messages; {}'.format(frommsg))
    print()
    
    sys.stdout.flush()
    sys.stderr.flush()

class Simulator:
  def __init__(self, num_nodes, talk_matrix):
    assert(len(talk_matrix) == num_nodes)
  
    self.num_nodes = num_nodes
    self.talk_matrix = [ [bool(x) for x in y] for y in talk_matrix ]
    self.processes = [None] * num_nodes
    self.out_pipes = [None] * num_nodes
    self.in_pipes = [None] * num_nodes
    
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
          for j, opipe in enumerate(self.out_pipes):
            if self.can_talk(i, j):
              opipe.send((i, msg))
    
if __name__ == '__main__':
  freeze_support()
  s = Simulator(NUM_NODES, CAN_TALK)
  s.start()