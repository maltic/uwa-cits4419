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
    dsr.ID = 1
    dsr2 = DSR(self)
    dsr2.ID = 2
    dsr.send_message("test packet", 2)
    while true:
      dsr.update()
      dsr2.update()
      msgs = dsr2.pop_messages()
      if msgs != []:
        print("Messages receied by dsr2 : {}".format(msgs))
      
     
    
  
  
