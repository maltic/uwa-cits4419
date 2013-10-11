import dsr

class TestNet:
  def __init__(self):
    self.dsr1 = dsr.DSR(self, 1)
    self.dsr2 = dsr.DSR(self, 2)
  def send(self, msg, addr):
    if addr == 1:
      self.dsr1.receive_packet(msg)
    elif addr == 2:
      self.dsr2.receive_packet(msg)
    elif addr == -1:
      print("tn: broadcasting {}".format(msg))
      self.dsr1.receive_packet(msg)
      self.dsr2.receive_packet(msg)
  def runSim(self):
    self.dsr1.send_message("test packet", 2)
    while True:
      self.dsr1.update()
      self.dsr2.update()
      msgs = self.dsr2.pop_messages()
      if msgs != []:
        print("Messages receied by dsr2 : {}".format(msgs[0].contents))
        
if __name__ == '__main__':
  tn = TestNet()
  tn.runSim()
      
     
    
  
  
