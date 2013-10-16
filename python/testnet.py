import dsr

class TestNet:
  def __init__(self):
    self.dsr1 = dsr.DSR(self, 1)
    self.dsr2 = dsr.DSR(self, 2)
    self.dsr3 = dsr.DSR(self, 3)
  def send(self, msg, addr):
    self.dsr1.receive_packet(msg)
    self.dsr2.receive_packet(msg)
    self.dsr3.receive_packet(msg)
  def runSim(self):
    self.dsr1.send_message("test packet", 2)
    while True:
      self.dsr1.update()
      self.dsr2.update()
      self.dsr3.update()
      msgs = self.dsr2.pop_messages()
      if msgs != []:
        print("Messages receied by dsr2 : {} path was {}".format(msgs[0].contents, msgs[0].path))
        
if __name__ == '__main__':
  tn = TestNet()
  tn.runSim()
      
     
    
  
  
