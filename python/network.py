import socket
import select
import sys
import thread

# Client and server components rolled into one
# Server is started on a new thread and each of up to 10 concurrent connections are dealt with on their own threads.

input_buffer = []
host = ''
port = 6969
recv_buffer = 1024

def send(msg, addr):
	# writes max 1024 byte to the remote address
	
	sock = socket.socket()
	
	try:
		sock.connect(addr, port)
	except Exception, e:
		alert("didn't connect to server")
	
	sock.send(msg)
	
	sock.close()
	
	return

def recieve():
	ret = input_buffer
	input_buffer = []
	return ret

  
 def _init_server(host, port):
	
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.bind(host)
	sock.listen(5)
 
	while 1
		clientsock, addr = sock.accept()
		thread.start_new_thread(_server_handler, (clientsock, addr))
	
	
	return
  
 def _start_server():
 
	thread.start_new_thread(_init_server, (host, port))
	
	
	return

 def _server_handler(clientsock, addr):
 
	#receive some bytes
	while 1
		data = clientsock.recv(recv_buffer)
		if not data: break
	
	#append them to the buffer
	input_buffer.append(data)
	
	#end the client socket connection
	clientsock.close()

	return
	