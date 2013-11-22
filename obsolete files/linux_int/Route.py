import os, subprocess, re, shutil

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