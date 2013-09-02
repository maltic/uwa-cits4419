import dsr

class application:
    def __init__(self):
        self.buffer = []
        
    def send(self):
        msg = input("Message: ")
        toId = input("To: ")
        dsr.send(msg, toId)

    def receive(self):
        for (msg, senderId) in self.buffer:
            print(senderId+':', msg)
        self.buffer = []
        
