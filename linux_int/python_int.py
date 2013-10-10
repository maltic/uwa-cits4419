#!/usr/bin/env python

import socket
import threading
import Queue
import os, subprocess, re, shutil
from struct import *

buffer = None
defaultSocket = None

HOST = "localhost"
PORT = 70000
REC_PORT = 71000
PROM_PORT = 72000

PROTOCOL_VALUE = 70


class Packet :
	
	def __init__(self, packet) :
		
		#raw data for re-sending
		self.packet			= packet[0]
		self.packet_meta		= packet[1]
		
		#Ethernet
		self.eth_header			= None
		self.eth_header_len		= None
		self.eth_protocol		= None
		self.eth_src			= None
		self.eth_dst			= None
		
		#IP
		self.ip_header			= None
		self.ip_header_len		= None
		self.ip_protocol		= None
		self.ip_ttl			= None
		self.ip_src			= None
		self.ip_dst			= None
		
		#TCP
		#UDP
		#ICMP
		
		packet = packet[0]
		
		#parse the ethernet header
		self.eth_header_len = 14
		eth = packet[:self.eth_header_len]
		self.eth_header = unpack('!6s6sH', eth)
		
		self.eth_protocol = socket.ntohs(self.eth_header[2])
		self.eth_dst = self.eth_addr(packet[0:6])
		self.eth_src = self.eth_addr(packet[6:12])
		
		#parse the IP header
		if self.eth_protocol == 8 :
			#IP header
			rawHeader = packet[self.eth_header_len:20+self.eth_header_len]
			#rawHeader = packet[0:20]
			
			self.ip_header = unpack('!BBHHHBBH4s4s' , rawHeader)
			
			version_ihl = self.ip_header[0]
			version = version_ihl >> 4
			ihl = version_ihl & 0xF
			self.eth_header_len = ihl * 4
		
			self.ip_ttl = self.ip_header[5]
			self.ip_protocol = self.ip_header[6]
			self.ip_src = socket.inet_ntoa(self.ip_header[8])
			self.ip_dst = socket.inet_ntoa(self.ip_header[9])
			
			#print 'Source: ' + str(self.ip_src) + ' Dest: ' + str(self.ip_dst) + ' Protocol: ' + str(self.ip_protocol)
	
	def eth_addr (self, a) :
		b = "%.2x-%.2x-%.2x-%.2x-%.2x-%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]),ord(a[4]) , ord(a[5]))
		return b

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


#Taken from http://www.shallowsky.com/software/netscheme/netutils-1.4.py
class Route :
	"""Network routing table entry: one line from route -n"""
	
	# Route(line)
	# Route(dest, gateway, iface, mask=None) :
	def __init__(self, *args) :
		if len(args) == 1 :
			self.init_from_line(args[0])
			return
		
		(self.dest, self.gateway, self.iface) = args
		#if len(args) > 3 :
		self.mask = "255.255.255.255"
	
	def init_from_line(self, line) :
		"""init from a line from route -n, such as:
			192.168.1.0     *               255.255.255.0   U         0 0          0 eth0
			default         192.168.1.1     0.0.0.0         UG        0 0          0 wlan0
			"""
		# Another place to get this is /proc/net/route.
		
		words = line.split()
		if len(words) < 8 :
			self.dest = None
			return
		self.dest = words[0]
		if self.dest == 'Destination' :
			self.dest = None
			return
		self.gateway = words[1]
		self.mask = words[2]
		self.iface = words[7]
	
	def __repr__(self) :
		"""Return a string representing the route"""
		return "dest=%-16s gw=%-16s mask=%-16s iface=%s" % (self.dest, self.gateway, self.mask, self.iface)
	
	def call_route(self, cmd) :
		"""Backend routine to call the system route command.
			cmd is either "add" or "delete".
			Users should normally call add() or delete() instead."""
		args = [ "route", cmd ]
		
		# Syntax seems to be different depending whether dest is "default"
		# or not. The man page is clear as mud and explains nothing.
		if self.dest == 'default' or self.dest == '0.0.0.0' :
			# route add default gw 192.168.1.1
			# route del default gw 192.168.160.1
			# Must use "default" rather than "0.0.0.0" --
			# the numeric version results in "SIOCDELRT: No such process"
			args.append("default")
				
			if self.gateway :
				args.append("gw")
				args.append(self.gateway)
		else :
			# route add -net 192.168.1.0 netmask 255.255.255.0 dev wlan0
			args.append('-net')
			args.append(self.dest)

			if self.gateway :
				args.append("gw")
				args.append(self.gateway)

			if self.mask :
				args.append("netmask")
				args.append(self.mask)

		args.append("dev")
		args.append(self.iface)
		
		print "Calling:", args
		subprocess.call(args)
	
	def add(self) :
		"""Add this route to the routing tables."""
		self.call_route("add")
	
	def delete(self) :
		"""Remove this route from the routing tables."""
		# route del -net 192.168.1.0 netmask 255.255.255.0 dev wlan0
		self.call_route("del")
	
	@staticmethod
	def read_route_table() :
		"""Read the system routing table, returning a list of Routes."""
		proc = subprocess.Popen('route -n', shell=True, stdout=subprocess.PIPE)
		stdout_str = proc.communicate()[0]
		stdout_list = stdout_str.split('\n')
		
		rtable = []
		for line in stdout_list :
			r = Route(line)
			if r.dest :
				rtable.append(r)
		
		return rtable


#def testFunction() :
#	rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
#	rawSocket.bind(("lo", 0x0003))
#
#	i = 10
#
#	buffer = PacketBuffer()
#
#	while i > 0 :
#		pkt = rawSocket.recvfrom(65565)
#	
#		print pkt
#	
#		packet = Packet(pkt)
#	
#		buffer.add(packet)
#	
#		print "Added Packet to buffer: " +  str(packet.ip_dst)
#
#		i = i - 1
#
#		print i
#
#	#print buffer
#	#print buffer.qMap['74.125.237.130']
#	list1 =  buffer.qMap.keys()
#	print list1
#
#	route = Route("8.8.8.8", "10.211.55.1", "eth0")
#	route.add()
#	buffer.release('8.8.8.8', rawSocket)
#
#
#testingThread = threading.Thread(target=testFunction)
#testingThread.start()


#--------------------------------------------------------------------------------------------------------------

def sendRouteRequestForDestination(destination, socket) :
	#do some things
	print "Sending RRQ for: " + str(destination)

	socket.sendto(destination, (HOST, PORT))

	#add the destination to a list of sent requests

def receiveRouteAction() :

	receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	receiveSocket.bind((HOST, REC_PORT))
	
	while True :
		data = receiveSocket.recvfrom(65535)

		#do something with the data
		#data = action-destination-gw
		#e.g. "add-192.168.1.0-10.211.55.1"
		#e.g. "del-192.168.1.0-10.211.55.1"
		
		print "Rec Route Act: data: " + str(data)

		destination = "192.168.1.0"
		gateway = "10.211.55.1"
		action = "add"
		
		if action == "add" :
			receiveRouteAdd(destination, gateway)
		elif action == "del" :
			receiveRouteDel(destination, gateway)


def receiveRouteAdd() :
	
	print "Adding Route: dst: " + destination + " gw: " + gateway
	
	newRoute = Route(destination, gateway, "eth0")
	newRoute.add()

	buffer.release(destination, defaultSocket)
	#remove the destination from the list


def receiveRouteDel(destination, gateway) :
	
	print "Deleting Route: dst: " + destination + " gw: " + gateway

	oldRoute = Route(destination, gateway, "eth0")
	oldRoute.delete()


#sets up the socket for default packets and listens for them.
def defaultPacketInterception() :
	#open up a raw socket to the loopback interface.
	global defaultSocket
	defaultSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
	defaultSocket.bind(("lo:0", 0x0003))
	
	#open a socket to the routing daemon
	routingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#init out buffer
	global buffer
	buffer = PacketBuffer()

	#start receiving packets
	while True :

		#get a packet from the socket (blocks waiting)
		pkt = defaultSocket.recvfrom(65565)
		
		#parse the packet into it's nice fields
		packet = Packet(pkt)
		
		#get the destination of the packet
		destination = packet.ip_dst
		
		#send route request message to the routing daemon
		if packet.ip_dst != "10.211.55.4" and packet.ip_src != "127.0.0.1"  and packet.ip_dst != "127.0.0.1":
			sendRouteRequestForDestination(destination, routingSocket)
		
			print "Def Rec Pkt: src: " + packet.ip_src + " dst: " + packet.ip_dst

			#add the packet to our buffer
			buffer.add(packet)
	#end while


def listenForPromisc() :

	promiscSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
	promiscSocket.bind(("eth0", 0x0003))

	#open a socket to the daemon
	daemonSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	while True :
		#process each packet and look for a specific protocol value
		pkt = promiscSocket.recvfrom(65565)

		packet = Packet(pkt)
		
		print "Promisc Rec Pkt: src: " + str(packet.ip_src) + " dst: " + str(packet.ip_dst) + " proto: " + str(packet.ip_protocol)

		if(packet.ip_protocol == PROTOCOL_VALUE) :
			#this is interesting to us.
			promiscSocket.sendto(packet.packet, (HOST, PROM_PORT))




# Main Code
defaultThread = threading.Thread(target=defaultPacketInterception)
defaultThread.start()

routeAddThread = threading.Thread(target=receiveRouteAction)
routeAddThread.start()

promiscThread = threading.Thread(target=listenForPromisc)
promiscThread.start()













