import sys
import dsr
import socket
import threading
import time


#Sub-class the UDP server and enable threading
#class ServerThreaded(socketserver.ForkingMixIn, socketserver.UDPServer):
#	pass

#Subclass the base handler and add our functionality.
#class ReceiveHandler(socketserver.BaseRequestHandler):
#	
#	def handle(self):
#		data = self.request[0].strip()
#		pkt = CustPacket.CustPacket(data)
#		
#		#extract out DSR string
#		dsr_data = pkt.udp_data
#		
#		global input_buffer
#		
#		input_buffer.append(dsr_data)
#
#		print("recieved something!!")
#
#end def

#end class

class Network:
	def __init__(self, ip_address, dsr_port) :

		#self.wireless_interface = wlan_int
		self.ip_address = ip_address
		self.dsr_port = dsr_port

		tokens = ip_address.split(".")
		self.id = tokens[3]
		self.net_prefix = tokens[0] + "." + tokens[1] + "." + tokens[2] + "."
		
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		#setup sending socket
		self.input_buffer = []

		self.server_thread = threading.Thread(target=self.serve_socket)
		self.server_thread.start()
	
#		server = ServerThreaded((ip_address, dsr_port), ReceiveHandler)
#		ip, port  = server.server_address
#		server_thread = threading.Thread(target=server.serve_forever)
#		server_thread.start()

	def receive(self) :
		ret = self.input_buffer
		self.input_buffer = []
		return ret

	def send(self, msg, addr) :
		if addr == -1 :
		#			dst_addr = self.net_prefix + "255"
			dst_addr = "255.255.255.255"
		else :
			dst_addr = self.net_prefix + str(addr)

		#pkt = IP(dst=dst_addr)/UDP(dport=self.dsr_port, sport=RandNum(1024,65535))/msg

		#send(pkt)
		print("NET: sending '" + str(msg) + "' to " + str(dst_addr))
		
		
		self.send_socket.sendto(bytes(msg,'UTF-8'), (dst_addr, self.dsr_port))

	def serve_socket(self):

		print("Starting socket server...")
		self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		self.recv_socket.bind(('0.0.0.0', self.dsr_port))

		while True:
			message, address = self.recv_socket.recvfrom(1024)
			
			if address[0] != self.ip_address:
					self.input_buffer.append(message.decode(encoding="UTF-8"))
#main loop

arg_address = sys.argv[1]
node_id = arg_address[-1:]

dsr = dsr.DSR(int(node_id))

network = Network(arg_address, 1069)

while True:
	
	user_msg = "hello from " + str(node_id)
	
	if node_id == "1":
		user_dst = 2
	else:
		user_dst = 1
	
	print("Sending message '" + user_msg + "' to dst: " + str(user_dst))

	dsr.send_message(user_msg, user_dst)

	dsr.update()
	dsr.update()
	dsr.update()

	dsrOutbox = dsr.pop_outbox()

	if dsrOutbox != []:
		print("DSR Outbox: " + str(dsrOutbox))

	for o in dsrOutbox:
		network.send(o[0], o[1])

	networkInput = network.receive()

	if networkInput != []:
				
		for m in networkInput:
			print("Received Message: '" + str(m) + "'")
			dsr.receive_packet(m)

	dsr.update()
	dsr.update()
	dsr.update()

	time.sleep(4)












