import socket
from struct import *

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
		self.udp_header_len		= None
		self.udp_src_port 		= None
		self.udp_dst_port		= None
		self.udp_length			= None
		self.udp_data			= None
		self.udp_data_len		= None
		
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
			self.ip_header_len = ihl * 4
		
			self.ip_ttl = self.ip_header[5]
			self.ip_protocol = self.ip_header[6]
			self.ip_src = socket.inet_ntoa(self.ip_header[8])
			self.ip_dst = socket.inet_ntoa(self.ip_header[9])
			
			#print 'Source: ' + str(self.ip_src) + ' Dest: ' + str(self.ip_dst) + ' Protocol: ' + str(self.ip_protocol)


		if self.ip_protocol == 17 :
			currentLength = self.eth_header_len + self.ip_header_len
			self.udp_header_len = 8
			udpHeaderRaw = packet[currentLength:currentLength+8]

			#unpack the header
			udp_header = unpack('!HHHH', udpHeaderRaw)
			self.udp_src_port = udp_header[0]
			self.udp_dst_port = udp_header[1]
			self.udp_length = udp_header[2]

			currentLength = self.eth_header_len + self.ip_header_len + self.udp_header_len
			self.udp_data_len = len(packet) - currentLength
			self.udp_data = packet[self.udp_data_len:]

			#print "UDP Src: " + str(self.udp_src_port) + " Dst: " + str(self.udp_dst_port) + " Len: " + str(self.udp_data_len) + " Data: "  + str(self.udp_data)
			
		
	
	def eth_addr (self, a) :
		b = "%.2x-%.2x-%.2x-%.2x-%.2x-%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]),ord(a[4]) , ord(a[5]))
		return b