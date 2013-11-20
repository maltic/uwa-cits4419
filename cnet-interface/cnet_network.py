import os
import sys
import time
import string
lib_path = os.path.abspath('../python')
sys.path.append(lib_path)
from dsr import DSR
from dsr_packet import DSRMessageType
from dsr_packet import Packet

#The routing process:
#cnet app layer makes a string message
#this is pushed to dummy-net new_message queue
#periodically dummy-net checks its queues
#unrouted queue has received, packeted messages from other nodes
#all new messages go to dsr
#all things in unrouted queue go to dsr
#pop the out_box to get messages that need broadcasting
#pop the in_box to get messages for the application layer


my_dsr = None
tmpfile = None
outfd = 0
infd = 0
in_pipe = None
out_pipe = None
nodeID = 0
char_encoding = 'utf-8'


class InterfacePacketType:
  MSG = 0
  PKT = 1

class InterfacePacket:
  def __init__(self, t, contents):
    self.type = t
    self.contents = contents

def send():
  rec = my_dsr.pop_inbox()
  fwd = my_dsr.pop_outbox()
  #write messages to pipe
  #tmpfile.write("MY INBOX CONTAINS: " + str(rec) + "\n")
  for msg in rec:
    tosend = "MSG." + msg.contents + "\n"
    tmpfile.write("RECEIVING A MESSAGE: " + msg.contents + "\n")
    #tmpfile.write("ENCODED MESSAGE: " + str(tosend.encode(char_encoding)) + "\n")
    os.write(outfd,"MSG.".encode(char_encoding))
    os.write(outfd,msg.contents.encode('ascii'))
    os.write(outfd,"\0".encode(char_encoding))
  for pkt in fwd:
    tmpfile.write("FORWARDING A MESSAGE: " + str(pkt[0]) + "\n")
    tosend = "FWD." + str(pkt[0]) + "\n"
    os.write(outfd,tosend.encode(char_encoding))


def receive():
  message = read_from_pipe(infd)
  if(message != ""):
    tmpfile.write(message + "\n")
    #if a new message call send_message
    #if a packeted message call receive_packet
    tokens = message.split(".")
    if(tokens[0] == "MSG"):
      tmpfile.write("that was a new message for " + tokens[2] + "\n")
      my_dsr.send_message(tokens[1],int(tokens[2]))
    elif(tokens[0] == "PKT"):
      tmpfile.write("that was a packet\n")
      my_dsr.receive_packet(tokens[1])
    else:
      tmpfile.write("that was something weird\n")
  if(message == "shutdown"):
    sys.exit()
  

def read_from_pipe(pipefd):
  #TODO buffer all the bytes before encoding and decoding
  #tmpfile.write("READING\n")
  next_char = ''
  msg = []
  while(next_char != "\n"):
    #tmpfile.write(next_char)
    
    try:
      next_byte = os.read(pipefd,1)
      next_char = next_byte.decode(char_encoding)
      if next_char != "\n":
      	msg.extend(next_byte)
    except OSError as e:
      #tmpfile.write(e.strerror + "\n")
      return ""
    except UnicodeDecodeError as e:
      next_char = ""
      continue
  return bytearray(msg).decode(char_encoding)

if __name__ == "__main__":
  
  
  infileName = sys.argv[1]
  outfileName = sys.argv[2]
  
  tmpfile = open(infileName[len(infileName)-1] + "tmp","w")
  
  nodeID = int(infileName[len(infileName)-1]);
  infd = os.open(infileName, os.O_NONBLOCK | os.O_RDWR)
  outfd = os.open(outfileName, os.O_NONBLOCK | os.O_RDWR)
  #in_pipe = os.fdopen(infd,"r");
  #out_pipe = os.fdopen(outfd,"w");
  
  tmpfile.write("In Pipe = " + infileName + "\nOut Pipe = " + outfileName + "\n")
  
  my_dsr = DSR(nodeID)
  
  
  #will have to loop over these read calls
  bytes = os.write(outfd,"HELLO\0".encode(char_encoding))
  #tmpfile.write("Wrote " + str(bytes) + " bytes\n")
  bytes = os.write(outfd,"BEEPBOOP\0".encode(char_encoding))
  #tmpfile.write("Wrote " + str(bytes) + " bytes\n")
  
  
  while(True):
    receive()
    my_dsr.update()
    send()
    time.sleep(1.0)
  #receive(infd, tmpfile)
  
  #os.close(outfd)
  #close(in_pipe)
  #close(out_pipe)
