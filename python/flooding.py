#a basic passthrough routing engine that ensures that all messages are broadcast

import network
import threading

input_buffer = []

def send(msg, recepient)

	#no route lookup done here just sent the destiantion as 255.255.255.255 and send.
	network.send(msg, '255.255.255.255')

#end def

def receive():
	ret = input_buffer
	input_buffer = []
	
	return ret

#end def


#basic run loop for processing receives.
while 1
	input_buf = network.receive()

	
	
	
