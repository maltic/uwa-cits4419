#Need to consider exponential back off limit for initiating new route discoveries
#Keep broken routes in cache for certain time? So that broken link request wont be forwarded
#How long to keep cached routes for?
#Shortening of routes by gratious reply?
#Piggyback route error msgs on a node's new route request.

import network

# Throws an exception if something goes wrong, otherwise returns nothing
def send(msg, recipient):
	# Call network
	return

# Returns [("Message 1', 1), ('Message 2', 2), ...]
# A list of tuples of the format (msg, sender)
# If there are no messages, the function will return an empty list
def recieve():
	# Call network
	return []

class DSR(object):
	route_cache = []
	address_table = []
	msg_id_table = []
	msg_buffer = []
	timelimit = 5
	exponetial_backoff_time = 0
	hop_limit = 3
	max_num_retransmission = 5
	
	
	def __init__(self):
		self.address = "blah"
	
	def run(self):
		while True:
			process_msg_buffer()
			#scan medium for messages
			if got_msg_in_medium():
				msg = get_msg();
				if msg == "route request":
					route_request(msg)
				elif msg == "route reply":
					route_reply(msg, msg.route, False)
				elif msg == "data packet":
					deliver_data(msg, msg.route)
				elif msg == "route error":
					route_error(msg, False)
				else:
					route_maintenance(msg.route)
				route_maintenance(msg.route)

#these need fleshing out with implementations:
def got_msg_in_medium(self):
	return True

def get_msg(self):
	return "hello"

#leave out route-cache stuff for now.
def route_cache_remove(self, broken_link):
	pass

def determine_broken_link(self, msg):
	return "hello"

def process_msg_buffer(self):
	if len(self.msg_buffer) > 0:
		for msg in self.msg_buffer:
			if msg.timeinbuffer > self.time_limit:
				self.msg_buffer.remove(msg)
		
		msg = self.msg_buffer[0]
		del self.msg_buffer[0]
		dest = msg.destination
		if route_cache_contains(dest):
			route = route_cache_finds(dest)
			forward(msg, route)
		else:
			route_discovery(msg)

def route_cache_contains(self, destination):
	return True

def route_cache_finds(self, destination):
	return ""

#call down to the network.send() function
def forward(self, msg, route):
	pass

#flesh this out
def broadcast(self, msg, type):
	pass

#check for a DSR identifier of some sort in the data received.
def is_data_packet(self, msg):
	return True


def route_discovery(self, msg):
	#do something regarding exponetial back off
	#to limit how fast new route discovery is performed for 'old' messages in buffer
	request_msg = route_request_msg(msg, msg.dest)
	request_msg.hopcount = 0
	request_msg.hoplimit = self.hop_limit
	broadcast(request_msg, "Request")

class route_request_msg(object):
	def __init__(self, msg, dest):
		self.msg = msg
		self.dest = dest

class route_reply_msg(object):
	def __init__(self, msg, dest):
		self.msg = msg
		self.dest = dest

class route_error_msg(object):
	def __init__(self, broken_link):
		self.broken_link = broken_link


def route_request(self, msg):
	route_maintenance(msg.route)
	
	if msg.dest == "ME":
		route_reply(msg, "Empty", False)
	elif msg.sourceroute.has(self):
		del msg
	elif msg.id in self.msg_id_table:
		del msg
	elif msg.hop_count > msg.hop_limit:
		del msg
	elif route_cache_contains(msg.destination):
		route = route_cache_finds(msg.dest)
		route_reply(msg, route, True)
	else:
		msg.route_add(self.address)
		msg.hop_count_increment()
		broadcast(msg, "Request")

def route_reply(self, msg, route, fromcache):
	#Need some sort of delay to limit how fast a route reply is sent back
	#To prevent a route reply storm
	if got_msg_in_medium():
		nmsg = get_msg();
		if is_data_packet(nmsg):
			if (nmsg.dest == msg.dest) and (nmsg.source == msg.source):
				return
	#Dont send route reply as the initiator have received a (possible shorter)
	#route reply and is transmitting the intended packet
	
	if route.empty:
		route = msg.sourceroute.reverse
		reply_msg = route_reply_msg(msg,route)
		forward(reply_msg, route)
	else:
		if fromcache:
			route = route.reverse + msg.sourceroute.reverse
		reply_msg = route_reply_msg(msg,route)
		forward(reply_msg, route)

def route_error(self, msg, issource):
	if issource:
		pass
		broken_link = determine_broken_link(msg)
		route_cache_remove(broken_link)
		error_msg = route_error_msg(broken_link)
		broadcast(error_msg, "error")
	else:
		pass
		broken_link = determine_broken_link(msg)
		route_cache_remove(broken_link)
		broadcast(msg, "error")
	
	if msg.iniator_address == self.address:
		process_msg_buffer()


def deliver_data(self, msg, route):
	if msg.dest == self.address:
		pass
	#senf to application layer
	else:
		num_times_transmitted = 0;
		while (num_times_transmitted < self.max_num_retransmissions):
			forward(msg, route)
			got_msg_in_medium()
			nmsg = get_msg()
			if nmsg.type == "Acknowledgemet":
				break
			else:
				num_times_transmitted=+1
		
		if (num_times_transmitted > self.max_num_retransmissions):
			route_error(msg, True)

def route_maintenance(self, route):
	pass
