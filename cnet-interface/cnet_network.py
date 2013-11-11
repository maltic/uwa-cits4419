import os
import sys

#def send(msg, addr):
  

#def receive():
  

def read_from_pipe(pipefd):
  msg = ""
  next_char = ""
  try:
    next_char = os.read(pipefd,1)
    
  except OSError:
    return ""
  msg = msg + next_char
  if(next_char != ""):
    while(next_char != "\n"):
      try:
        next_char = os.read(pipefd,1)
      except OSError:
        break
      msg = msg + next_char
  return msg

if __name__ == "__main__":
  
  
  infileName = sys.argv[1]
  outfileName = sys.argv[2]
  infd = os.open(infileName, os.O_NONBLOCK | os.O_RDWR)
  outfd = os.open(outfileName,os.O_NONBLOCK | os.O_RDWR)
  #in_pipe = os.fdopen(infd,"r");
  #out_pipe = os.fdopen(outfd,"w");
  
  
  tmpfile = open(infileName[len(infileName)-1] + "tmp","w")
  tmpfile.write("Before input\n")
  message = ""
  
  #will have to loop over these read calls
  message = read_from_pipe(infd)
  tmpfile.write(message)
  message = read_from_pipe(infd)
  tmpfile.write(message)
  tmpfile.write("After input\n")
  bytes = os.write(outfd,"HELLO\0")
  tmpfile.write("Wrote " + str(bytes) + " bytes\n")
  bytes = os.write(outfd,"BEEPBOOP\0")
  tmpfile.write("Wrote " + str(bytes) + " bytes\n")
  #os.close(outfd)
  #close(in_pipe)
  #close(out_pipe)
