#!/usr/bin/env python

import socket
import threading
import Packet
import Route
import PacketBuffer
import time

buffer = None
defaultSocket = None
rreqList= []

HOST = "localhost"
DSR_PORT = 60000
ACT_PORT = 61000
PROM_PORT = 62000

PROTOCOL_VALUE = 60000
EXPIRE_REQ_TIMER = 30




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
	
	#check if destination is in the list
	for index, value in enumerate(rreqList) :
		if destination == rreqList[index][0] :
			#print "DEF: destination " + destination + " is in the list"
			return None
	
	#do some things
	print "ROUT_T: Sending RRQ for: " + str(destination) + " on UDP " + str(DSR_PORT)

	socket.sendto(destination, (HOST, DSR_PORT))
	
	#add the destination to a list of sent requests
	curTime = time.time()
	rreqList.append( (destination, curTime) )
					
	#find the expired request - ie older than EXPIRE_REQ_TIMER
	for index, value in enumerate(rreqList) :
		if curTime - rreqList[index][1] > EXPIRE_REQ_TIMER :
			print "ROUT_T: Expiring request to destination " + rreqList[index][0]
			del rreqList[index]



def receiveRouteAction() :

	receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	receiveSocket.bind((HOST, ACT_PORT))
	
	while True :
		data = receiveSocket.recvfrom(65535)
		
		print "ROUT_T: Recieved Route Action on UDP " + str(ACT_PORT) + ": (" + str(data) + ")"

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


def receiveRouteAdd(destination, gateway) :
	
	print "ROUT_T: Adding Route: dst: " + destination + " gw: " + gateway
	
	newRoute = Route.Route(destination, gateway, "eth0")
	newRoute.add()

	buffer.release(destination, defaultSocket)
	#remove the destination from the list


def receiveRouteDel(destination, gateway) :
	
	print "ROUT_T: Deleting Route: dst: " + destination + " gw: " + gateway

	oldRoute = Route.Route(destination, gateway, "eth0")
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
	buffer = PacketBuffer.PacketBuffer()

	#start receiving packets
	while True :

		#get a packet from the socket (blocks waiting)
		pkt = defaultSocket.recvfrom(65565)
		
		#parse the packet into it's nice fields
		packet = Packet.Packet(pkt)
		
		#get the destination of the packet
		destination = packet.ip_dst
		
		#send route request message to the routing daemon
		if packet.ip_dst != "10.211.55.4" and packet.ip_src != "127.0.0.1"  and packet.ip_dst != "127.0.0.1":
			sendRouteRequestForDestination(destination, routingSocket)
		
			print "DEFAULT: Rec Pkt: src: " + packet.ip_src + " dst: " + packet.ip_dst
			
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

		packet = Packet.Packet(pkt)
		
		#print "PROMISC: Rec Pkt: src: " + str(packet.ip_src) + " dst: " + str(packet.ip_dst) + " proto: " + str(packet.ip_protocol)


		if(packet.ip_protocol == 17) :
			#print "PROMISC: Rec Pkt: src: " + str(packet.ip_src) + " dst: " + str(packet.ip_dst) + " proto: " + str(packet.ip_protocol)
			print "PROMIS: UDP: dst_port: " + str(packet.udp_dst_port) + " UDP Data: " + str(packet.udp_data)

		if(packet.udp_dst_port == PROTOCOL_VALUE) :
			#this is interesting to us.
			
			print "PROMISC: Heard DSR packet: src: " + str(packet.ip_src) + " dst: " + str(packet.ip_dst) + " data: " + packet.udp_data
			
			promiscSocket.sendto(packet.packet, (HOST, PROM_PORT))




# Main Code
defaultThread = threading.Thread(target=defaultPacketInterception)
defaultThread.start()

routeAddThread = threading.Thread(target=receiveRouteAction)
routeAddThread.start()

promiscThread = threading.Thread(target=listenForPromisc)
promiscThread.start()













