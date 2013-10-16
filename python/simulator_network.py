from threading import Timer

class SimulatorNetwork:
  def __init__(self, q, dsr):
    self.out_p = q[0]
    self.in_p = q[1]
    self.dsr = dsr
    self.stop = False
    self._on_recieve()
    
  def _on_recieve(self):
    print('NETWORK: Triggered _on_recieve')
    inp = self.receive()
    for a, p in inp:
      self.dsr.receive_packet(p)
     
    if not self.stop:	 
      print('NETWORK: Rerunning timer')
      t = Timer(1, self._on_recieve)
      t.start()
    
  def stop_timer(self):
    self.stop = True

  def send(self, msg, addr):
    p = (addr, msg)
    print('NETWORK: Message out: {}'.format(p))
    self.out_p.send(p)

  # Returns a list of (fromaddr, msg)
  def receive(self):
    out = []
    while self.in_p.poll():
      out.append(self.in_p.recv())
   
    print('NETWORK: Messages in: {}'.format(out)) 
    return out
