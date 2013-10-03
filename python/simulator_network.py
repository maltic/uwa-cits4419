

class SimulatorNetwork:
  def __init__(self, q):
    self.out_p = q[0]
    self.in_p = q[1]

  def send(self, msg, addr):
    self.out_p.send((addr, msg))

  # Returns a list of (fromaddr, msg)
  def receive(self):
    out = []
    while self.in_p.poll():
      out.append(self.in_p.recv())
    return out