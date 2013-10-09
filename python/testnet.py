import dsr

class TestNet:
  def __init__(self):
    pass
  def send(msg, addr):
    if addr == 1:
      dsr.receive_packet(msg)
    elif addr == 2:
      dsr2.receive_packet(msg)
  def runSim():
    dsr = DSR(self)
    dsr2 = DSR(self)
    while true:
      dsr.update()
      dsr2.update()
      dsr.send_packet("test packet", 2)
      
     
    
  
  
