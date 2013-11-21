#==================================README=======================================
#
#This is a DSR protocol implementation using Python.
#
#It is the project for CITS4419 - Mobile and Wireless Computing
#at The University of Western Australia.
#
#<AUTHOR> = Ash Tyndall, Asra Alshabib, Bo Chuen Chung, Dayang Abang Mordian,
#           Hui Li Leow, Max Ward, Raphael Byrne, Timothy Raphael,
#           Vincent Sun, Zhiqiang (Cody) Qiu
#
#<SUPERVISOR> = Prof. Amitava Datta
#
#<ORGANIZATION> = The University of Western Australia
#
#<YEAR> = 2013
#
#<VERSION> = V1.0
#
#===============================================================================

#=================================BSD LICENSE===================================
#
#Copyright (c) <YEAR>, <AUTHOR>
#
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  - Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#===============================================================================

import socket
import threading
import CustPacket
import Route
import PacketBuffer
import SocketServer
from dsr import DSR
from scapy.all import *

# Client and server components rolled into one
# Server is started on a new thread and each of up to 10 concurrent connections are dealt with on their own threads.

default_packet_buffer = []
dsr_input_buffer = []

DSR_PORT = 1069
LOG = True

#Default Packet Interception
buffer = None
defaultSocket = None
destinationWaitingList = []

#Managing Routes
currentRoutes = []


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

	global dsr_input_buffer

	dsr_input_buffer.append(dsr_data)
  #end def

#end class


class Network:
	def __init__(self, ip_address, wlan_int, dsr):
		
		
		self.wireless_interface = wlan_int
		self.ip_address = ip_address
		
		tokens = ip_address.split(".")
		self.id = tokens[3]
		self.net_prefix = tokens[0] + "." + tokens[1] + "." + tokens[2] + "."
		
		self.dsr = dsr
	
		server = ServerThreaded((ip_address, DSR_PORT), ReceiveHandler)
		ip, port  = server.server_address
		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.start()

		defaultThread = threading.Thread(target=self.defaultPacketInterception)
		defaultThread.start()
	
		#promiscThread = threading.Thread(target=listenForPromisc)
		#promiscThread.start()

		# some scapy setup
		conf.iface = self.wireless_interface

	def receive(self):
		global dsr_input_buffer
		ret = dsr_input_buffer
		dsr_input_buffer = []

		return ret

	def send(self, msg, addr):
	
		#generate packet
		if addr == 255 :
			dst_addr = "255.255.255.255"
		else :
			dst_addr = self.net_prefix + addr
	
		pkt = IP(dst=dst_addr)/UDP(dport=DSR_PORT, sport=RandNum(1024,65535))/msg
	
	
		send(pkt)
			
	#empty the input_buffer and deliver messages to DSR
	def deliverDSRPackets(self):
	
		buffer = self.receive()
		
		for dsr_msg in buffer:
			self.dsr.receive_packet(dsr_msg.data)

	
	#sets up the socket for default packets and listens for them.
	def defaultPacketInterception(self) :
		#open up a raw socket to the loopback interface.
		global defaultSocket
		defaultSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
		defaultSocket.bind(("lo:0", 0x0003))
	
		#init out buffer
		global buffer
		buffer = PacketBuffer.PacketBuffer()
	
		#start receiving packets
		while True :
		
			#get a packet from the socket (blocks waiting)
			pkt = defaultSocket.recvfrom(65565)
		
			#parse the packet into it's nice fields
			packet = CustPacket.CustPacket(pkt)
		
			#get the destination of the packet
			destination = packet.ip_dst
		
			#send route request message to the routing daemon
			if packet.ip_dst != "10.211.55.4" and packet.ip_src != "127.0.0.1"  and packet.ip_dst != "127.0.0.1":
				self.dsr.__route_discovery(packet.data, packet.ip_dst[-1:])
			
				if LOG:
					print ("DEFAULT: Rec Pkt: src: " + packet.ip_src + " dst: " + packet.ip_dst)
			
				#add the packet to our buffer
				buffer.add(packet)

				#check to see if we're already waiting on this destination
				isThere = False
				global destinationWaitingList
				for dest in destinationWaitingList :
					if packet.ip_dst == dest :
						isThere = True
					
				if isThere == False:
					destinationWaitingList.append(packet.ip_dst)
		#end while


	def processRouteActions(self) :
		
		while True :
			#copy the destination waiting list
			global destinationWaitingList
			#add lock
			waitingList = list(destinationWaitingList)
			#remove lock
			
			#for each waiting prefix, attempt to get a shortest path for it.
			for prefix in waitingList:
				short_path = self.dsr.route_cache.get_shortest_path(prefix)
				
				routePresent = False
				for r in currentRoutes:
					if r[0] == prefix :
						routePresent = True
				
				if routePresent == False :
					routeAdd(prefix, short_path[0])
					currentRoutes.add((prefix, short_path[0]))
			
				#add lock
				destinationWaitingList.remove(prefix)
				#remove lock
			
			#do route maintenance
			
			#for each route, check it against the route cache
			for route in currentRoutes:
				cachedShortest = self.dsr.route_cache.get_shortest_path(route[0])
				
				if cachedShortest == None:
					#remove route, no longer current.
					routeDel(route[0], route[1])
					currentRoutes.remove((route[0], route[1]))
				
				#route is current (matches)
				#if route[1] == cachedShortest[0]:
					#do nothing

				#route has changed
				if route[1] != cachedShortest[0] :
					routeDel(route[0], route[1])
					routeAdd(route[0], cachedShortest[0])
					currentRoutes.add((route[0], cachedShortest[0]))
				

	def routeAdd(destinationID, gatewayID) :
	
		destination = NET_PREFIX + str(destinationID)
		gateway = NET_PREFIX + str(gatewayID)

		print "ROUT_T: Adding Route: dst: " + destination + " gw: " + gateway
	
		newRoute = Route.Route(destination, gateway, NET_IFACE)
		newRoute.add()
		#add to our own current route tracking
	
		buffer.release(destination, defaultSocket)
		#remove the destination from the list


	def routeDel(destinationID, gatewayID) :
		
		destination = NET_PREFIX + str(destinationID)
		gateway = NET_PREFIX + str(gatewayID)
	
		print "ROUT_T: Deleting Route: dst: " + destination + " gw: " + gateway
	
		oldRoute = Route.Route(destination, gateway, NET_IFACE)
		oldRoute.delete()






#DSR Run loop
dsr = DSR(4)
network = Network("10.211.55.4", "eth0", dsr)

while True:
	network.deliverDSRPackets()
	network.processRouteActions()





