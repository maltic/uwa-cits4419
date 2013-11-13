input_buffer = []
LOG = True
import Packet
import sys
import dsr
#from scapy.all import *
import socketserver
import socket
import threading


#Sub-class the UDP server and enable threading
class ServerThreaded(socketserver.ForkingMixIn, socketserver.UDPServer):
	pass

#Subclass the base handler and add our functionality.
class ReceiveHandler(socketserver.BaseRequestHandler):
	
	def handle(self):
		data = self.request[0].strip()
		pkt = CustPacket.CustPacket(data)
		
		#extract out DSR string
		dsr_data = pkt.udp_data
		
		global input_buffer
		
		input_buffer.append(dsr_data)
#end def

#end class

class Network:
	def __init__(self, ip_address, dsr_port) :

		#self.wireless_interface = wlan_int
		self.ip_address = ip_address

		tokens = ip_address.split(".")
		self.id = tokens[3]
		self.net_prefix = tokens[0] + "." + tokens[1] + "." + tokens[2] + "."
		
		#setup sending socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		server = ServerThreaded((ip_address, dsr_port), ReceiveHandler)
		ip, port  = server.server_address
		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.start()

	def receive(self) :
		global input_buffer
		ret = input_buffer
		input_buffer = []

	def send(self, msg, addr) :
		if addr == 255 :
			dsr_add = "255.255.255.255"
		else :
			dst_addr = self.net_prefix + addr

		#pkt = IP(dst=dst_addr)/UDP(dport=self.dsr_port, sport=RandNum(1024,65535))/msg

		#send(pkt)
		self.socket.sendto(msg, (dst_addr, self.dsr_port))


#main loop

dsr = dsr.DSR(1)
network = Network("10.211.55.4", 1069)
msgNumber = 1
loop_number = 0

while True:
	
	if loop_number == 50000:
		user_msg = "hello" + str(msgNumber)
		msgNumber += 1
	
		user_dst = 1
	
		print("Sending message '" + user_msg + "' to dst: " + str(user_dst))

		dsr.send_message(user_msg, user_dst)

		loop_number = 0

	else :
		loop_number = loop_number + 1

	dsr.update()
	
	input = network.receive()

	if input != None:
		
		print("got some shiz from the network" + str(input))
		
		for m in input:
			full_packet = Packet(m)
			dsr.receive_packet(full_packet.udp_data)












