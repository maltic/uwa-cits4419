#==================================README=======================================
#
#This is a DSR protocol implementation using Python.
#
#It is the project for CITS4419 - Mobile and Wireless Computing
#at The University of Western Australia.
#
#<AUTHOR> = Ash Tyndall, Asra Alsahib, Bo Chuen Chung, Dayang Abang Mordian,
#           Hui li Leow, Max Ward, Raphael Byrne, Timothy Raphael,
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
import socketserver

# Client and server components rolled into one
# Server is started on a new thread and each of up to 10 concurrent connections are dealt with on their own threads.

input_buffer = []
HOST = "localhost"
DSR_PORT = 70000
RECV_BUFFER = 1024
layerAbove = None

#Subclass the base handler and add our functionality.
class ReceiveHandler(socketserver.BaseRequestHandler):

  def handle(self):
  
    data = self.request[0].strip()

    layerAbove.receive_packet(data)
  
  #end def

#end class  

#Sub-class the UDP server and enable threading
class ServerThreaded(socketserver.ForkingMixIn, socketserver.UDPServer):
  pass
    
def send(msg, addr):
  # writes max 1024 byte to the remote address
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  #to enumlate a broadcast L2 network, just broadcast it at L3.
  #ignore the address that the user has sent to me.
  sock.sendto(msg, '255.255.255.255')
  
  print("sent message", msg)

  sock.close()
  
  return
  
#end def

def receive():
  ret = input_buffer
  input_buffer = []
  
  return ret
  
#end def

def init(dsr_ref):
  layerAbove = dsr_ref
  
  server = ServerThreaded((HOST, DSR_PORT), ReceiveHandler)
  ip, port  = server.server_address
  server_thread = threading.Thread(target=server.serve_forever)
  server_thread.start()

