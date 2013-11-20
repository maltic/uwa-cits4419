import sys
import dsr
import socket
import threading
import time
from datetime import datetime
from dsr_packet import Packet
from route_cache import RouteCache

DSR_PORT = 1069

LOG_BUFFER = []
DSR_TERMINAL_LOG_FLAG = False

TIMESTAMP_FORMAT = '%Y%m%d%H%M%S'
CURRENT_LOG_FILE = ""


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
	
	global CURRENT_LOG_FILE
	
	CURRENT_LOG_FILE = "dsr_log_" + str(get_timestamp()) + ".log"

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

		dsr_debug = dsr.pop_debug_buffer()

		global LOG_BUFFER
		global DSR_TERMINAL_LOG_FLAG
		
		if DSR_TERMINAL_LOG_FLAG == True:
			for msg in dsr_debug:
				write_message(msg)
			LOG_BUFFER.extend(dsr_debug)
		else:
			for msg in dsr_debug:
				write_message(msg)

		#output to the terminal
		for term_msg in LOG_BUFFER:
			print(term_msg)
		LOG_BUFFER = []



def print_help():
	print("Available Commands: ")
	print("-------------------")
	print("show route <id>                # Prints the current best route in the cache")
	print("show route-cache               # Prints the entire route cache to terminal")
	print("show route-cache <id>          # Prints the route cache to terminal for a given destination")
	print("show id                        # Prints the current node's ID")
	print("run test <id> <id> <id>        # sends test message to the following node IDs")
	print("run send '<msg>' <id>          # sends a message to a specific ID")
	print("set debug <on/off>             # Enable / Disable DSR terminal debugging")
	print("help                           # Prints this help message")
	print("exit                           # Exit the program")

def log_message(msg):
	global LOG_BUFFER
	LOG_BUFFER.append(msg)
	write_message(msg)

def write_message(msg):
	log_file = open(CURRENT_LOG_FILE, 'a')
	log_file.write(msg + "\n")
	log_file.close()


def get_timestamp():
	return datetime.now().strftime(TIMESTAMP_FORMAT)


#main loop
arg_address = sys.argv[1]

#get the last octet of the IP address supplied
tokens = arg_address.split(".")

#node id as a string
node_id = tokens[3]

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
	
	write_message("dsr-cli@" + hostname + "> " + user_input)
	
	input_tokens = user_input.split(" ")
	
	try:
		if input_tokens[0] == "show":
			if input_tokens[1] == "route":
				route_cache = dsr.get_route_cache()
				shortest_path = route_cache.get_shortest_path(int(input_tokens[2]))
				if shortest_path == None:
					log_message("Path doesn't exist in cache")
				else:
					log_message("Shortest Path to node: " + str(input_tokens[2]) + " is " + str(shortest_path))
			
			if input_tokens[1] == "route-cache":
				
				route_cache = dsr.get_route_cache()
				
				if len(input_tokens) == 2:
					log_message("Current Route Cache: " + str(route_cache.get_edge_list()))
				
				if len(input_tokens) > 2:
					try:
						val = int(input_tokens[2])
						log_message("Current Route Cache for ID " + str(input_tokens[2]) + ": " + str(route_cache.get_edge_list()[input_tokens[2]]))
					except ValueError:
						log_message("Input not a valid node ID")
				
			if input_tokens[1] == "id":
				log_message("Node ID: " + str(node_id))
	except IndexError:
		print_help()
	
	try:
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
					log_message("Input not a valid node ID")

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
					log_message("Input not a valid node ID")
	except IndexError:
		print_help()


	try:
		if input_tokens[0] == "set":
			if input_tokens[1] == "debug":
				if input_tokens[2] == "on":
					DSR_TERMINAL_LOG_FLAG = 1
					log_message("DSR Debugging enabled")
				elif input_tokens[2] == "off":
					DSR_TERMINAL_LOG_FLAG = 0
					log_message("DSR Debugging disabled")
				else:
					log_message("Unsupported input " + str(input_tokens[2]))

		if input_tokens[0] == "help":
			print_help()

		if input_tokens[0] == "exit":
			exit(0)
	except IndexError:
		print_help()
	
	if input_tokens[0] != "show" and input_tokens[0] != "run" and input_tokens[0] != "set" and input_tokens[0] != "help" and input_tokens[0] != "":
		log_message("Unsupported input '" + str(input_tokens[0]) + "'")
















