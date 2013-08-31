#import dsr

class application:
    def __init__(self):
        self.buffer = {}
        
    def send(self):
        msg = input("Message: ")
        toId = input("To: ")
        dsr.send(msg, toId)

    def receive(self):
        for sender in self.buffer:
            print(self.buffer[sender])
        self.buffer = {}
        
