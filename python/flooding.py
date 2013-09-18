#a basic passthrough routing engine that ensures that all messages are broadcast

import network
import threading
import socket, select

input_buffer = []
connection_list = []

def send(msg, recepient)
        for recipient in connection_list:
                try:
                        recipient.send(msg)
                except:
                        recipient.close()
                        connection_list.remove(recipient)
	

#end def

#receive connection and append the connection to the list
def receive(port):
        input_buffer = 4096
        
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(("0.0.0.0",port))
        sock.listen(10)'

        connection_list.append(sock)

        while 1:
                read_sockets,write_sockets,error_sockets
#end def
