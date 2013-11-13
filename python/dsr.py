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

#?????????????????????????????????WHICH LICENSE?????????????????????????????????
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
#?????????????????????????????????WHICH LICENSE?????????????????????????????????

#===========================PUBLIC INTERFACE====================================
#TODO
#===============================================================================


import simulator_network
import time
import ast
import route_cache
from dsr_packet import DSRMessageType, Packet

MAX_transmissions = 2
MAX_time_between_ack = 1
MAX_time_between_request = 1

#DSR Routing Algorithm
class DSR:
  #-----------------------------------------------------------
  #                    INITIALISATIONS
  #-----------------------------------------------------------
  #Initisalise itself with 5 queues - receive Q, send Q, send buffer, done buffer, and ack buffer.
  def __init__(self, node_addr):
    #self.network = simulator_network.SimulatorNetwork(net, self)
    self.next_packet_id = 0
    self.__receive_queue = []
    self.__send_queue = []
    self.__send_buffer = []
    self.__done_buffer = []
    self.__outbox = [] #packets ready to be sent on the network
    self.__awaiting_acknowledgement_buffer = []
    self.ID = node_addr
    self.__route_cache = route_cache.RouteCache(self.ID)
    self.__seen = {} # set of (id, fromID) tuples representing which pakcets have been seen already

  #Generate a DSR packet
  def __make_packet(self, type, path, contents):
    pkt = Packet()
    pkt.type = type
    pkt.path = path
    pkt.contents = contents
    pkt.id = self.next_packet_id
    pkt.originatorID = pkt.id
    self.next_packet_id += 1
    return pkt

  #Generate a DSR packet
  def __make_packet_o(self, type, path, contents, originator):
    pkt = Packet()
    pkt.type = type
    pkt.path = path
    pkt.contents = contents
    pkt.id = self.next_packet_id
    pkt.originatorID = originator
    self.next_packet_id += 1
    return pkt

  #-----------------------------------------------------------
  #                     NETWORK - SENDING
  #-----------------------------------------------------------
  #Broadcast the message to every node
  def __network_broadcast(self, pkt):
    pkt.fromID = -1
    pkt.toID = -1
    self.__outbox.append((str(pkt), -1))
    print("Broadcasting Packet {}".format(pkt))
    return

  #Send a packet to a given destination
  def __network_sendto(self, pkt, toID):
    pkt.fromID = self.ID
    pkt.toID = toID
    if pkt.type != DSRMessageType.ACK:
      self.__add_to_ack_buffer(pkt)
    self.__outbox.append((str(pkt), toID))
    print("Sending Packet of Type {} To {}  {}".format(pkt.type, toID, pkt))
    return

  #-----------------------------------------------------------
  #                   DSR - ROUTE REQUEST
  #-----------------------------------------------------------
  #There is no route currently stored in the cache, call this
  #funtction to discover a route the destination.
  def __route_request(self, msg):
    #print("Route request for ID {} with path {}".format(msg.contents, msg.path))
    if int(msg.contents) == self.ID:
      msg.path.append(str(self.ID))
      rev_path = list(reversed(msg.path))
      self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, rev_path, msg.path[0], msg.originatorID), int(rev_path[1]))
      #print("Sending route reply to {} via path {}".format(msg.path[0], rev_path))
    elif self.ID in [int(value) for value in msg.path]:
      #print("Route request: I'm already in the path {}".format(msg.path))
      #avoid cycles
      pass
    else:
      msg.path.append(str(self.ID))
      #print("Route request: Appending myself to path {}".format(msg.path))
      self.__network_broadcast(self.__make_packet_o(DSRMessageType.REQUEST, msg.path, msg.contents, msg.originatorID))

  #-----------------------------------------------------------
  #                   DSR - ROUTE REPLY
  #-----------------------------------------------------------
  #It hears a Route Request message.
  #If there is a route stored in the cache, then replies back with the route.
  #Otherwise broadcast the Route Request message to its neighbours.
  def __route_reply(self, msg):
    #if i am the originator of the message then remove it from the send buffer
    #if not, then send it to the next guy on the list
    #print("Route reply for {} with path {}".format(msg.contents, msg.path))
    if int(msg.contents) == self.ID:
      #print("This reply is for me from {}".format(msg.path[0]))
      rev_path = list(reversed(msg.path))
      next_index = 1
      contents = self.__remove_from_send_buffer(msg.originatorID)
      if contents == None:
        return
      if isinstance(contents, Packet):
        intpath = [int(value) for value in contents.path]
        index = intpath.index(self.ID)
        newpath = intpath[:index]
        newpath.extend(rev_path)
        contents.path = newpath
        self.__network_sendto(contents, int(rev_path[next_index]))
      else:
        self.__network_sendto(self.__make_packet(DSRMessageType.SEND, rev_path, contents), int(rev_path[next_index]))
      #print("Sending message {} to {} via path {}".format(contents, rev_path[next_index], rev_path))
    else:
      intpath = [int(value) for value in msg.path]
      next_index = intpath.index(self.ID)+1
      self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, msg.path, msg.contents, msg.originatorID), int(msg.path[next_index]))
      #print("This is not my route reply. Forwarding to {}".format(msg.path[next_index]))
    #need to start route discovery if a link is broken
    #i havn't added this yet because I am not sure how the network layer will let us know

  #-----------------------------------------------------------
  #                   DSR - ROUTE ERROR
  #-----------------------------------------------------------
  #Generate an error message if there is error reading cache
  def __route_error(self, msg):
      global DSRMessageType
      #self.__remove_from_cache(msg.contents)
      print("I should be printing an error message")
      print(msg)
      self.__network_broadcast(self.__make_packet(DSRMessageType.ERROR, msg.path, msg.contents))
    #not implemented yet, because there is not route cache


  def __route_send(self, msg):
    #if I am the recipient, yay! add it to the done_buffer
    #if not, send it to the next guy on the list

    #from_index = msg.path.index(self.ID)-1
    #__network_sendto(self.make_packet(DSRMessageType.ACK, msg.path, self.ID), msg.path[from_index])

    if int(msg.path[-1]) == self.ID:
      self.__done_buffer.append(msg)
    else:
      intpath = [int(value) for value in msg.path]
      next_index = intpath.index(self.ID)+1
      self.__network_sendto(self.__make_packet(DSRMessageType.SEND, msg.path, msg.contents), int(msg.path[next_index]))
    #need to start route discovery if a link is broken

  #-----------------------------------------------------------
  #                DSR - ROUTE DISCOVERY
  #-----------------------------------------------------------
  def __route_discover(self, msg, toID):
    #lookup route cache not implemented
    #start route discovery
    temp = self.__make_packet(DSRMessageType.REQUEST, [self.ID], toID)
    start = time.time()
    counter = 1
    self.__send_buffer.append((msg, temp.originatorID, start, counter))
    self.__network_broadcast(temp)

  #-----------------------------------------------------------
  #                DSR - ACKOWLEDGEMENT
  #-----------------------------------------------------------
  def __msg_acknowledgement(self, msg):
    for ack in self.__awaiting_acknowledgement_buffer:
      if int(ack[0].id) == int(msg.contents):
        print("Acknowledging packet {} in response to {}".format(ack[0], msg))
        self.__awaiting_acknowledgement_buffer.remove(ack)
        return

  #-----------------------------------------------------------
  #                   DSR - SENDING
  #-----------------------------------------------------------
  #Append the message to the send queue
  def send_message(self, contents, toID):
    self.__send_queue.append((contents, toID))

  #-----------------------------------------------------------
  #                 DSR - RECEIVING
  #-----------------------------------------------------------
  def receive_packet(self, pkt):
    a = Packet.from_str(pkt)
    if int(a.toID) != self.ID and int(a.toID) != -1:
        return #do promiscuous stuff
    self.__receive_queue.append(a)
    print(' ---NET--- {} Packet Received! {}'.format(self.ID, pkt))

  #pops all the messages this dsr node has received
  #and which were destined for it
  def pop_inbox(self):
    tmp = self.__done_buffer
    self.__done_buffer = []
    return tmp

  def pop_outbox(self):
    #print("testing2 ", self.__outbox)
    tmp = self.__outbox
    self.__outbox = []
    return tmp

  def __remove_from_send_buffer(self, ID):
    for send in self.__send_buffer:
      if send[1] == ID:
        msg = send[0]
        self.__send_buffer.remove(send)
        return msg
    return None

  #-----------------------------------------------------------
  #                     DSR - AWAITING
  #-----------------------------------------------------------
  def __check_ack_buffer(self):
    print("Checking ack buffer")
    print(self.__awaiting_acknowledgement_buffer)
    for ack in self.__awaiting_acknowledgement_buffer:
      if ack[2] > MAX_transmissions:
        print ("Giving up!")
        intpath = [int(value) for value in ack[0].path]
        next_index = intpath.index(self.ID)+1
        unreachable_node = ack[0].path[next_index]
        self.__network_broadcast(self.__make_packet(DSRMessageType.ERROR, [self.ID],  unreachable_node))
        self.__route_discover(ack[0], int(unreachable_node))
        self.__awaiting_acknowledgement_buffer.remove(ack)
      else:
        end = time.time()
        elapsed = end - int(ack[1])
        if elapsed > MAX_time_between_ack:
          msg = ack[0]
          intpath = [int(value) for value in ack[0].path]
          next_index = intpath.index(self.ID)+1
          self.__network_sendto(msg, int(msg.path[next_index]))
          print("Retransmitting")

  def __add_to_ack_buffer(self, pkt):
    for ack in self.__awaiting_acknowledgement_buffer:
      if ack[0] == pkt:
        start = time.time()
        timetransmitted = int(ack[2])+1
        self.__awaiting_acknowledgement_buffer.remove(ack)
        self.__awaiting_acknowledgement_buffer.append((pkt,start,timetransmitted))
        return
    start = time.time()
    self.__awaiting_acknowledgement_buffer.append((pkt,start,1))
    print("Adding to ack: {}".format(pkt))
    #print("Add pkt with originator ID {} to ack".format(pkt.originatorID))

  def __check_send_buffer(self):
    for send in self.__send_buffer:
      end = time.time()
      elapsed = end - int(send[2])
      if elapsed > MAX_time_between_request*send[3]:
        start = time.time()
        counter = int(send[3])+1
        msg = send[0]
        originatorID = send[1]
        self.__send_buffer.remove(send)
        self.__send_buffer.append((msg, originatorID, start, counter))

  #-----------------------------------------------------------
  #                     UPDATE
  #-----------------------------------------------------------
  #This method updates the node periodically
  def update(self):
    #self.__check_ack_buffer()
    self.__check_send_buffer()
    for msg in self.__receive_queue:
      #avoid self self messages
      if msg.fromID == self.ID:
        continue
      #send acknowledgement message back
      if msg.toID != -1 and msg.type != DSRMessageType.ACK: #-1 fromID means broadcast
        print("Sending acknowledgement for orginator ID {}".format(msg.originatorID))
        self.__network_sendto(self.__make_packet(DSRMessageType.ACK, [], msg.id), int(msg.fromID))
      if msg.type == DSRMessageType.REQUEST:
        self.__route_request(msg)
      elif msg.type == DSRMessageType.REPLY:
        self.__route_reply(msg)
      elif msg.type == DSRMessageType.ERROR:
        self.__route_error(msg)
      elif msg.type == DSRMessageType.SEND:
        self.__route_send(msg)
      elif msg.type == DSRMessageType.ACK:
        self.__msg_acknowledgement(msg)
    for send in self.__send_queue:
      self.__route_discover(send[0], send[1])
    self.__receive_queue = []
    self.__send_queue = []
    #need to add exponential backoff from acknoledgement messages and error propagation

