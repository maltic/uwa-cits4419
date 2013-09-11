import socket
import threading
import SocketServer

# Client and server components rolled into one
# Server is started on a new thread and each of up to 10 concurrent connections are dealt with on their own threads.

input_buffer = []
HOST = "localhost"
UDP_PORT = 6969
RECV_BUFFER = 1024

#Subclass the base handler and add our functionality.
class ReceiveHandler(SocketServer.BaseRequestHandler):

	def handle(self):
	
		data = self.request[0].strip()
		clientsock = self.request[1]
		
		input_buffer.append(data)
		
		print "Received data from {}".format(self.client_address[0])
		print data
	
	#end def

#end class	

#Sub-class the UDP server and enable threading
class ServerThreaded(SocketServer.ForkingMixIn, SocketServer.UDPServer):
	pass
		
def send(msg, addr):
	# writes max 1024 byte to the remote address
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#to enumlate a broadcast L2 network, just broadcast it at L3.
	#ignore the address that the user has sent to me.
	sock.sendto(msg, '255.255.255.255')
	
	print "sent message", msg

	sock.close()
	
	return
	
#end def

def receive():
	ret = input_buffer
	input_buffer = []
	
	return ret
	
#end def

	
# How to setup the server:
server = ServerThreaded((HOST, UDP_PORT), ReceiveHandler)
ip, port  = server.server_address
	
#Start server on it's own thread
#it'll spawn a new thread for each request
	
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()
print "Server Started..."


# How to use the 'Send()' function
send("message 1", ("localhost", 6969))
send("message 2", ("localhost", 6969))

