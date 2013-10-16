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
                   
            (3,  [ [1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1] ]),
                   
            (6,  [ [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 1, 0, 1, 1],
                   [1, 1, 1, 0, 1],
                   [1, 1, 1, 1, 0] ]),
                   
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
  print('SIMULATOR: Node {} online'.format(node_addr))

  d = dsr.DSR(q, node_addr)

  for i in range(loops):
    print('== LOOP {} =='.format(i))
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

  d.network.stop_timer()
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
              opipe.send((i, msg))
			  
    print('Completed. Consult logs at "{}" for more info'.format(self.comm_loc))

if __name__ == '__main__':
  freeze_support()
  s = Simulator(NUM_NODES, CAN_TALK, RUN_LOOPS, COMM_LOC)
  s.start()
