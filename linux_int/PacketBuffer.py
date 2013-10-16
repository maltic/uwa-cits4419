import Queue

class PacketBuffer :

	def __init__(self) :
		#setup the map with a sample queue.
		self.qMap = dict([('127.0.0.1', Queue.Queue())])

	def add(self, packet) :
		#check to see if queue exists for destination
		#if it exists, put packet onto the queue
		if self.qMap.has_key(packet.ip_dst) :
			queue = self.qMap[packet.ip_dst]
			queue.put_nowait(packet)
		else :
			#otherwise, create a new queue and add to that.
			self.qMap[packet.ip_dst] = Queue.Queue()
			queue = self.qMap[packet.ip_dst]
			queue.put_nowait(packet)

	def release(self, destination, socket) :
		if self.qMap.has_key(destination) :
			queue = self.qMap[destination]
			
			print queue
			
			while not queue.empty() :
				packet = queue.get()
				print packet.packet
				bytes = socket.send(packet.packet)
				print "Sent bytes: " + str(bytes)
			
			#for memory mangement
			del self.qMap[destination]
		else :
			print "No queue to empty"