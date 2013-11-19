import sys
import dsr
import socket
import threading
import time
from dsr_packet import Packet


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

	def receive(self) :
		ret = self.input_buffer
		self.input_buffer = []
		return ret

	def send(self, msg, addr) :
		if addr == -1 :
			dst_addr = "255.255.255.255"
		else :
			dst_addr = self.net_prefix + str(addr)

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


def run_background_updates(dsr, network):

	while True:
		#send messages on the network that are waiting in the outbox
		dsrOutbox = dsr.pop_outbox()

		for o in dsrOutbox:
			network.send(o[0], o[1])

		#run an update cycle
		dsr.update()

		#recieve messages from the network input buffer
		networkInput = network.receive()
	
		if networkInput != []:
			#give them to dsr to process
			for m in networkInput:
				dsr.receive_packet(m)

		#run an update cycle
		dsr.update()
		
		#see if we have any messages for the user.
		inbox = dsr.pop_inbox()

		#print to the console
		if inbox != []:
			#print("APP: Got Message: " + str(inbox))
			for pkt in inbox:
				app_msg = str(pkt.contents)
				msg_parts = app_msg.split("#")
				
				print(msg_parts[0] + "> " + msg_parts[1] + "\n")

#main loop
arg_address = sys.argv[1]

#get the last octet of the IP address supplied
tokens = arg_address.split(".")
node_id = tokens[3]

dsr = dsr.DSR(int(node_id))

network = Network(arg_address, 1069)


background_thread = threading.Thread(target=run_background_updates, args=(dsr, network))
background_thread.start()

user_name = input("Please set your name: ")

while True:
	
	print("\n-----------------------------------")
	print("\n          Application              ")
	print("\n-----------------------------------")
	user_msg = input("\nEnter message: ")
	user_dst = input("\nEnter destination id: ")
	print("\n-----------------------------------")
	
	app_msg = user_name + "#" + user_msg
	
	dsr.send_message(app_msg, user_dst)

















