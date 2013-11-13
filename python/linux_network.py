input_buffer = []
LOG = True
import Packet
import sys
import DSR
from scapy.all import *


#Sub-class the UDP server and enable threading
class ServerThreaded(SocketServer.ForkingMixIn, SocketServer.UDPServer):
	pass

#Subclass the base handler and add our functionality.
class ReceiveHandler(SocketServer.BaseRequestHandler):
	
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
	def __init__(self, ip_address, dsr_port)

		self.wireless_interface = wlan_int
		self.ip_address = ip_address

		tokens = ip_address.split(".")
		self.id = tokens[3]
		self.net_prefix = tokens[0] + "." + tokens[1] + "." + tokens[2] + "."

		self.dsr = dsr_instance

	def receive(self)
		global input_buffer
		ret = input_buffer
		input_buffer = []

	def send(self, msg, addr)
		if addr == 255 :
			dsr_add = "255.255.255.255"
		else :
			dst_addr = self.net_prefix + addr

		pkt = IP(dst=dst_addr)/UDP(dport=self.dsr_port, sport=RandNum(1024,65535))/msg

		send(pkt)


#main loop

dsr = DSR(1)
network = Network("10.1.1.1", 1069)

while True:
	
	#prompt the user
	user_msg = raw_input("Please enter the message to send: ")
	user_dst = raw_input("Please enter the destination ID : ")
	
	dsr.send_message(user_msg, user_dst)
	
	input = network.receive()

	for m in input:
		full_packet = Packet(m)
		dsr.receive_packet(full_packet.udp_data)











