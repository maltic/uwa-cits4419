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


import time
import route_cache
from dsr_packet import DSRMessageType, Packet

MAX_transmissions = 3
MAX_time_between_ack = 1.5
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
    # set of route reqs which have already been seen
    # we should probably be expiring old entries from the bellow buffer
    self.__seen_route_requests = set()
    self.__already_received_msgs = set()
    
  def __debug_print(self, contents):
    print(contents)

  #Generate a DSR packet
  def __make_packet(self, type, path, contents):
    pkt = Packet()
    pkt.type = type
    pkt.path = path
    pkt.contents = contents
    pkt.id = self.next_packet_id
    pkt.originatorID = pkt.id
    pkt.originatorNodeID = self.ID
    self.next_packet_id += 1
    return pkt

  #Generate a DSR packet
  def __make_packet_o(self, type, path, contents, originator, origantorNode):
    pkt = Packet()
    pkt.type = type
    pkt.path = path
    pkt.contents = contents
    pkt.id = self.next_packet_id
    pkt.originatorID = originator
    pkt.originatorNodeID = origantorNode
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
    #self.__debug_print("Broadcasting Packet {}".format(pkt))
    return

  #Send a packet to a given destination
  def __network_sendto(self, pkt, toID):
    pkt.fromID = self.ID
    pkt.toID = toID
    self.__outbox.append((str(pkt), toID))
    self.__debug_print("Sending Packet of Type {} To {}  {}".format(pkt.type, toID, pkt))
    return

  #-----------------------------------------------------------
  #                   DSR - ROUTE REQUEST
  #-----------------------------------------------------------
  #There is no route currently stored in the cache, call this
  #funtction to discover a route the destination.
  def __route_request(self, msg):
  
    self.__route_cache.remove_link(msg.brokenLink[0], msg.brokenLink[1])
    
    rr_ident = (msg.path[0], msg.originatorID) #identifier of rreq
    #self.__debug_print("Route request for ID {} with path {}".format(msg.contents, msg.path))
    if int(msg.contents) == self.ID:
      msg.path.append(str(self.ID))
      rev_path = list(reversed(msg.path))
      self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, rev_path, msg.path[0], msg.originatorID, msg.originatorNodeID), int(rev_path[1]))
      #self.__debug_print("Sending route reply to {} via path {}".format(msg.path[0], rev_path))
    elif self.ID in [int(value) for value in msg.path] or rr_ident in self.__seen_route_requests :
      #avoid cyclic requests, and already seen requests
      pass
    else:
      #add to buffer of route requests already seen
      self.__seen_route_requests.add(rr_ident)
      #NOTE: Could add a route cache lookup here
      msg.path.append(str(self.ID))
      #self.__debug_print("Route request: Appending myself to path {}".format(msg.path))
      #self.__network_broadcast(self.__make_packet_o(DSRMessageType.REQUEST, msg.path, msg.contents, msg.originatorID))
      pkt = self.__make_packet_o(DSRMessageType.REQUEST, msg.path, msg.contents, msg.originatorID,msg.originatorNodeID)
      pkt.brokenLink = msg.brokenLink
      #self.__debug_print("Route request: Appending myself to path {}".format(msg.path))
      self.__network_broadcast(pkt)
      
  #-----------------------------------------------------------
  #                   DSR - ROUTE REPLY
  #-----------------------------------------------------------
  #It hears a Route Request message.
  #If there is a route stored in the cache, then replies back with the route.
  #Otherwise broadcast the Route Request message to its neighbours.
  def __route_reply(self, msg):
    #if i am the originator of the message then remove it from the send buffer
    #if not, then send it to the next guy on the list
    #self.__debug_print("Route reply for {} with path {}".format(msg.contents, msg.path))
    if int(msg.contents) == self.ID:
      #self.__debug_print("This reply is for me from {}".format(msg.path[0]))
      rev_path = list(reversed(msg.path))
      next_index = 1
      contents = self.__remove_from_send_buffer(msg.originatorID)
      
      self.__debug_print("Route reply contents: {}".format(contents))
      
      #skip messages we already sent
      if contents == None:
        return
        
      pkt = self.__make_packet(DSRMessageType.SEND, rev_path, contents)
      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
      
      self.__network_sendto(pkt, int(rev_path[next_index]))
      #self.__debug_print("Sending message {} to {} via path {}".format(contents, rev_path[next_index], rev_path))
    else:
      intpath = [int(value) for value in msg.path]
      next_index = intpath.index(self.ID)+1
      self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, msg.path, msg.contents, msg.originatorID,msg.originatorNodeID), int(msg.path[next_index]))
      #self.__debug_print("This is not my route reply. Forwarding to {}".format(msg.path[next_index]))
      


  def __route_send(self, msg):
    #if I am the recipient, yay! add it to the done_buffer
    #if not, send it to the next guy on the list

    #from_index = msg.path.index(self.ID)-1
    #__network_sendto(self.make_packet(DSRMessageType.ACK, msg.path, self.ID), msg.path[from_index])
    
    #acknowledge previous sender
    self.__network_sendto(self.__make_packet(DSRMessageType.ACK, [], msg.id), int(msg.fromID))

    if int(msg.path[-1]) == self.ID:
      #NOTE: need to make sure we dont re-add messages we already received
      if (msg.originatorID, msg.originatorNodeID) in self.__already_received_msgs:
        return
      self.__already_received_msgs.add((msg.originatorID, msg.originatorNodeID))
      self.__done_buffer.append(msg)
    else:
      intpath = [int(value) for value in msg.path]
      print(str(intpath))
      next_index = intpath.index(self.ID)+1
      pkt = self.__make_packet_o(DSRMessageType.SEND, msg.path, msg.contents, msg.originatorID, msg.originatorNodeID)
      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
      self.__network_sendto(pkt, int(msg.path[next_index]))
    #need to start route discovery if a link is broken

  #-----------------------------------------------------------
  #                DSR - ROUTE DISCOVERY
  #-----------------------------------------------------------
  def __route_discover(self, data, toID):
  
    #first attempt to use route cache
    cached_path = self.__route_cache.get_shortest_path(int(toID))
    self.__debug_print(str(self.__route_cache.get_edge_list()))
    self.__debug_print("Cached Path: " + str(cached_path))
    if cached_path:
      self.__debug_print("Found path to {} using route cache... {}".format(toID, cached_path))
      pkt = self.__make_packet(DSRMessageType.SEND, cached_path, data)
      self.__network_sendto(pkt, int(cached_path[1]))
      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
    else:
      #start route discovery
      temp = self.__make_packet(DSRMessageType.REQUEST, [self.ID], toID)
      start = time.time()
      #add too send buffer
      #this ensures that we re-broadcast rreqs that are taking too long
      self.__send_buffer.append((data, temp, start, 1))
      self.__network_broadcast(temp)
    
    
  #-----------------------------------------------------------
  #        DSR - ROUTE DISCOVERY WITH ERROR PROPAGATION
  #-----------------------------------------------------------
  def __route_discover_with_error(self, originalPkt, brokenLink):
    self.__debug_print("route discovery with error")
    #remove broken link from cache
    self.__route_cache.remove_link(brokenLink[0], brokenLink[1])
    #start route discovery
    temp = self.__make_packet(DSRMessageType.REQUEST, [self.ID], originalPkt.toID)
    temp.originatorID = originalPkt.originatorID
    temp.originatorNodeID = originalPkt.originatorNodeID
    
    #propagate the broken link
    #so that others can remove it from their route cache
    temp.brokenLink = brokenLink

    start = time.time()
    #add too send buffer
    #this ensures that we re-broadcast rreqs that are taking too long
    self.__send_buffer.append((originalPkt.contents, temp, start, 1))
    self.__network_broadcast(temp)


  #-----------------------------------------------------------
  #                DSR - ACKOWLEDGEMENT
  #-----------------------------------------------------------
  def __msg_acknowledgement(self, msg):
    for ack in self.__awaiting_acknowledgement_buffer:
      if int(ack[0].id) == int(msg.contents):
        self.__debug_print("Acknowledging packet {} in response to {}".format(ack[0], msg))
        self.__awaiting_acknowledgement_buffer.remove(ack)
        return

  #-----------------------------------------------------------
  #                   DSR - SENDING
  #-----------------------------------------------------------
  #Append the message to the send queue
  def send_message(self, contents, toID):
    self.__send_queue.append((contents, toID))
    self.__debug_print("DSR sending message '" + str(contents) + "'")

  #-----------------------------------------------------------
  #                 DSR - RECEIVING
  #-----------------------------------------------------------
  def receive_packet(self, pkt):
    a = Packet.from_str(pkt)
      
    #dont add self messages to route cache (this should never happen, but just in case)
    if int(a.fromID) != self.ID and len(a.path) > 1:
        #add new paths to route cache
        self.__route_cache.offer_route(a.path)
        
    #ignore messages that arent for us
    if int(a.toID) != self.ID and int(a.toID) != -1 :
      return
        
    self.__receive_queue.append(a)
    self.__debug_print(' ---NET--- {} Packet Received! {}'.format(self.ID, pkt))

  #pops all the messages this dsr node has received
  def pop_inbox(self):
    tmp = self.__done_buffer
    self.__done_buffer = []
    return tmp
  
  #pops all the messages the dsr node wishes to send on the network
  def pop_outbox(self):
    tmp = self.__outbox
    self.__outbox = []
    return tmp
  
  #remove some packet by id from the send buffer, and get its contents back
  def __remove_from_send_buffer(self, ID):
    for send in self.__send_buffer:
      if send[1].originatorID == ID:
        self.__send_buffer.remove(send)
        return send[0] #return the data/contents associated with that route request
    return None

  #-----------------------------------------------------------
  #                     DSR - AWAITING
  # checks the acknowledge buffer, and retransmits unacknowledge packets
  # eventually will restart a route request, and propagate the broken link
  #-----------------------------------------------------------
  def __check_ack_buffer(self):
	  #self.__debug_print("Checking ack buffer")
	  #self.__debug_print(self.__awaiting_acknowledgement_buffer)
    toAdd = []
    for ack in self.__awaiting_acknowledgement_buffer:
      if ack[2] > MAX_transmissions:
        self.__debug_print ("Giving up {}!".format(ack))
        intpath = [int(value) for value in ack[0].path]
        next_index = intpath.index(self.ID)+1
        unreachable_node = ack[0].path[next_index]
        
        #sending error packets in depreciated
        #self.__network_broadcast(self.__make_packet(DSRMessageType.ERROR, [self.ID],  unreachable_node))
        
        #do a route discovery with error propagation
        self.__route_discover_with_error(ack[0], (self.ID, int(unreachable_node)))
        
        #remove from waiting for acknowledgement
        self.__awaiting_acknowledgement_buffer.remove(ack)
      else:
        end = time.time()
        elapsed = end - int(ack[1])
        if elapsed > MAX_time_between_ack:
          msg = ack[0]
          intpath = [int(value) for value in ack[0].path]
          next_index = intpath.index(self.ID)+1
          self.__network_sendto(msg, int(msg.path[next_index]))
          self.__debug_print("-----Elapsed: {}.   Retransmitting {}, resend {} times".format(elapsed, msg, ack[2]))
          #remove old record
          self.__awaiting_acknowledgement_buffer.remove(ack)
          #add to buffer again with updated transmissions
          toAdd.append((ack[0],time.time(),ack[2]+1))
    self.__awaiting_acknowledgement_buffer.extend(toAdd)

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
    self.__debug_print("Adding to ack: {}".format(pkt))
    #self.__debug_print("Add pkt with originator ID {} to ack".format(pkt.originatorID))

  def __check_send_buffer(self):
    for send in self.__send_buffer:
      end = time.time()
      elapsed = end - int(send[2])
      if elapsed > MAX_time_between_request*send[3]:
        self.__debug_print("Re route requesting for packet {}".format(send[1]))
        #recalculated counters and time
        start = time.time()
        counter = int(send[3])+1
        contents = send[0]
        #reinsert the packet into the send buffer and re-broadcast it
        self.__send_buffer.remove(send)
        self.__send_buffer.append((send[0], send[1], start, counter))
        self.__network_broadcast(send[1])

  #-----------------------------------------------------------
  #                     UPDATE
  #-----------------------------------------------------------
  #This method updates the node periodically
  def update(self):
    self.__check_ack_buffer()
    self.__check_send_buffer()
    for msg in self.__receive_queue:
      #avoid self self messages
      if msg.fromID == self.ID:
        continue
      if msg.type == DSRMessageType.REQUEST:
        self.__route_request(msg)
      elif msg.type == DSRMessageType.REPLY:
        self.__route_reply(msg)
      elif msg.type == DSRMessageType.SEND:
        self.__route_send(msg)
      elif msg.type == DSRMessageType.ACK:
        self.__msg_acknowledgement(msg)
      else:
        self.__debug_print("!!!!!!!! UNEXPECTED PACKET TYPE")
    for send in self.__send_queue:
      self.__route_discover(send[0], send[1])
    self.__receive_queue = []
    self.__send_queue = []

