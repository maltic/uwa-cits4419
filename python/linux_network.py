import sys
import dsr
import socket
import threading
import time
from dsr_packet import Packet

DSR_PORT = 1069


class Network:
	def __init__(self, ip_address, dsr_port) :
		
		self.ip_address = ip_address
		self.dsr_port = dsr_port
		
		#parse the IP address, last octet is our id, first 3 are the prefix
		tokens = ip_address.split(".")
		self.id = tokens[3]
		self.net_prefix = tokens[0] + "." + tokens[1] + "." + tokens[2] + "."
		
		#setup the socket, allow broadcasts and socket reuse.
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		#setup sending socket
		self.input_buffer = []

		self.run_flag = threading.Event()
		self.run_flag.set()
		
		#setup background thread for serving the socket
		self.server_thread = threading.Thread(target=self.serve_socket)
		self.server_thread.daemon = True
		self.server_thread.start()

	def receive(self) :
		#method to easily clear the receive buffer
		ret = self.input_buffer
		
		#reset the buffer
		self.input_buffer = []
		
		return ret

	def send(self, msg, addr) :
		#dsr protocol says -1 is a broadcast
		if addr == -1 :
			dst_addr = "255.255.255.255"
		else :
			#append the prefix to create a routeable address.
			dst_addr = self.net_prefix + str(addr)
		
		#send the data on the UDP socket, force UTF-8 encoding.
		self.send_socket.sendto(bytes(msg,'UTF-8'), (dst_addr, self.dsr_port))

	def serve_socket(self):

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

#node id as a string
node_id = tokens[3]

#dsr debug state
dsr_debug = 0

dsr = dsr.DSR(int(node_id))

network = Network(arg_address, DSR_PORT)

hostname = socket.gethostname()

run_event = threading.Event()
run_event.set()
background_thread = threading.Thread(target=run_background_updates, args=(dsr, network))
background_thread.daemon = True
background_thread.start()

while True:
	
	user_input = input("dsr-cli@" + hostname + "> ")
	user_input = user_input.strip()
	
	input_tokens = user_input.split(" ")
	
	if input_tokens[0] == "show":
		#if input_tokens[1] == "route":
			#shortest_path = dsr.__route_cache.get_shortest_path(int(input_tokens[2]))
			#print("Shortest Path to node: " + str(input_tokens[2]) + " is " + str(shortest_path))
		
		#if input_tokens[1] == "route-cache":
			#route_cache = dsr.route_cache.get_edge_list()
			#print("Current Route Cache: " + str(route_cache))
			
		if input_tokens[1] == "id":
			print("Node ID: " + str(node_id))
	
	if input_tokens[0] == "run":
		if input_tokens[1] == "test":
			
			length = len(input_tokens) - 1

			#ensure our input is good.
			try:
				#not the best, but allows me to check input before processing.
				for i in range (2, length):
					val = int(input_tokens[i])
				for i in range (2, length):
					dsr.send_message("Test Message from " + str(node_id) + " to " + input_tokens[i], input_tokens[i])
			except ValueError:
				print("Input not a valid node ID")

		if input_tokens[1] == "send":
			
			first_index = 0
			last_index = 0
			
			#find the message amoungst the tokens
			for j in range(2, len(input_tokens)-1):
				tok_len = len(input_tokens[j])-1
				#check for a string termination character (")
				if input_tokens[j][0] == '"':
					first_index = j
				if input_tokens[j][tok_len] == '"':
					last_index = j

			message = ""

			if first_index != 0 and last_index != 0:
				for tok in range(first_index, last_index+1):
					message = message + str(input_tokens[tok])

			message = message.strip('"')

			try:
				val = int(input_tokens[last_index + 1])
				dsr.send_message(message, input_tokens[last_index + 1])
			except ValueError:
				print("Input not a valid node ID")


	if input_tokens[0] == "set":
		if input_tokens[1] == "debug":
			if input_tokens[2] == "on":
				dsr_debug = 1
				print("DSR Debugging enabled")
			if input_tokens[2] == "off":
				dsr_debug = 0
				print("DSR Debugging disabled")

	if input_tokens[0] == "help":
		print("Available Commands: ")
		print("-------------------")
		print("show route <id>                # Prints the current best route in the cache")
		print("show route cache               # Prints the entire route cache to terminal")
		print("show id                        # Prints the current node's ID")
		print("run test <id> <id> <id>        # sends test message to the following node IDs")
		print("run send '<msg>' <id>          # sends a message to a specific ID")
		print("set debug <on/off>             # Enable / Disable DSR terminal debugging")
		print("help                           # Prints this help message")
		print("exit                           # Exit the program")

	if input_tokens[0] == "exit":
		exit(0)


	if dsr_debug == 1:
		debug_output = dsr.pop_debug_buffer()

		for msg in debug_output:
			print("DSR: " + str(msg))















