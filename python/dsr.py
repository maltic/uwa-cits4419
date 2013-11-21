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

import time
import route_cache
from dsr_packet import DSRMessageType, Packet

#you will need to fiddle with these settings
#depending on the speed of your simulator/computer/network

#maximum retransmissions of a packet to get an acknowledgement before it is dropped
MAX_transmissions = 3
#maximum time to wait for an acknowledgement
MAX_time_between_ack = 1.5    #in seconds
#maximum wait time before route discovery is retried
MAX_time_between_request = 2  #in seconds
#maximum number of route discovery retries
MAX_route_discoveries = 3

#DSR Routing Algorithm
class DSR:
  #-----------------------------------------------------------
  #                    INITIALISATIONS
  #-----------------------------------------------------------
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
    self.__seen_route_requests = set()
    # set of message ids which we have already succesfully received
    self.__already_received_msgs = set()
    self.__debug_buffer = []

  def __debug_print(self, contents):
    print(contents)

  def __log(self, contents):
    self.__debug_buffer.append("DSR LOG: " + contents)

  def pop_debug_buffer(self):
    ret = self.__debug_buffer
    self.__debug_buffer = []
    return ret


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

  #Return the RouteCache on request
  def get_route_cache(self):
    return self.__route_cache

  #-----------------------------------------------------------
  #                     NETWORK - SENDING
  #-----------------------------------------------------------
  #Broadcast the message to every node
  def __network_broadcast(self, pkt):
    pkt.toID = -1
    self.__outbox.append((str(pkt), -1))
    self.__log("Broadcasting packet {}.".format(pkt.pretty_print()))
    return

  #Send a packet to a given destination
  def __network_sendto(self, pkt, toID):
    pkt.fromID = self.ID
    pkt.toID = toID
    self.__outbox.append((str(pkt), toID))
    self.__log("Directly sending packet: {}".format(pkt.pretty_print()))
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
      self.__log("Route request processed, sending reply in response to packet {}.".format(msg.pretty_print()))
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

      #used a cached path if one exists and there is no broken link in the packet
      cached_path = self.__route_cache.get_shortest_path(int(msg.contents))
      if cached_path and msg.brokenLink == (-1,-1) :
        self.__log("Route request {} processed, found a complete path in the route cache {}.".format(msg.pretty_print(), cached_path))
        msg.path.extend(cached_path)
        rev_path = list(reversed(msg.path))
        next = rev_path.index(self.ID)+1
        self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, rev_path, msg.path[0], msg.originatorID, msg.originatorNodeID), int(rev_path[next]))
      else:
        self.__log("Propagating route request {}.".format(msg.pretty_print()))
        msg.path.append(str(self.ID))
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

      self.__log("Received route reply for packet {}.".format(msg.pretty_print()))

      #skip messages we already sent
      if contents == None:
        return

      pkt = self.__make_packet_o(DSRMessageType.SEND, rev_path, contents, msg.originatorID, msg.originatorNodeID)
      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send

      self.__network_sendto(pkt, int(rev_path[next_index]))
      #self.__debug_print("Sending message {} to {} via path {}".format(contents, rev_path[next_index], rev_path))
    else:
      self.__log("Forwarding route reply for packet {}.".format(msg.pretty_print()))
      intpath = [int(value) for value in msg.path]
      next_index = intpath.index(self.ID)+1
      self.__network_sendto(self.__make_packet_o(DSRMessageType.REPLY, msg.path, msg.contents, msg.originatorID,msg.originatorNodeID), int(msg.path[next_index]))
      #self.__debug_print("This is not my route reply. Forwarding to {}".format(msg.path[next_index]))


  #What to do with messages of type SEND
  def __route_send(self, msg):
    #if I am the recipient, yay! add it to the done_buffer
    #if not, send it to the next guy on the list

    #acknowledge previous sender
    self.__network_sendto(self.__make_packet(DSRMessageType.ACK, [], msg.id), int(msg.fromID))

    if int(msg.path[-1]) == self.ID:
      #NOTE: need to make sure we dont re-add messages we already received
      if (msg.originatorID, msg.originatorNodeID) in self.__already_received_msgs:
        return
      self.__already_received_msgs.add((msg.originatorID, msg.originatorNodeID))
      self.__log("End of send chain {}.".format(msg.pretty_print()))
      self.__done_buffer.append(msg)
    else:
      self.__log("Forwarding in send chain {}.".format(msg.pretty_print()))
      intpath = [int(value) for value in msg.path]
      next_index = intpath.index(self.ID)+1

      #attempt the route shortening optimization
      destinationID = len(msg.path)-1
      cached_path = self.__route_cache.get_shortest_path(int(msg.path[destinationID]))
      if cached_path:
        cached_length = len(cached_path) - 1
        left = len(intpath) - next_index
        #use the cached path if it is shorter
        if cached_length < left:
          pkt = self.__make_packet_o(DSRMessageType.SEND, cached_path, msg.contents, msg.originatorID, msg.originatorNodeID)
          self.__log("Found a better path for send chain: {}.".format(cached_path))
          self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
          self.__network_sendto(pkt, int(cached_path[1]))
          return


      pkt = self.__make_packet_o(DSRMessageType.SEND, msg.path, msg.contents, msg.originatorID, msg.originatorNodeID)

      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
      self.__network_sendto(pkt, int(msg.path[next_index]))
    #need to start route discovery if a link is broken

  #-----------------------------------------------------------
  #                DSR - ROUTE DISCOVERY
  #-----------------------------------------------------------
  def __route_discover(self, data, destinationID):
    self.__log("Attempting route discovery to {}.".format(destinationID))
    #first attempt to use route cache
    cached_path = self.__route_cache.get_shortest_path(int(destinationID))
    if cached_path:
      self.__log("Found path to {} using route cache: {}".format(destinationID, cached_path))
      pkt = self.__make_packet(DSRMessageType.SEND, cached_path, data)
      self.__network_sendto(pkt, int(cached_path[1]))
      self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
    else:
      #start route discovery
      temp = self.__make_packet(DSRMessageType.REQUEST, [self.ID], destinationID)
      start = time.time()
      #add too send buffer
      #this ensures that we re-broadcast rreqs that are taking too long
      self.__send_buffer.append((data, temp, start, 1))
      self.__network_broadcast(temp)


  #-----------------------------------------------------------
  #        DSR - ROUTE DISCOVERY WITH ERROR PROPAGATION
  #-----------------------------------------------------------
  #remember the original pkt is always a SEND packet
  def __route_discover_with_error(self, originalPkt, brokenLink):
    self.__log("Attempting route discovery (with error propagation of link {}) to {}.".format(brokenLink, originalPkt.toID))
    #remove broken link from cache
    self.__route_cache.remove_link(brokenLink[0], brokenLink[1])

    destinationID = originalPkt.path[len(originalPkt.path)-1]

    # Should never use cached_path since broken link will never get propagated
    #cached_path = self.__route_cache.get_shortest_path(int(destinationID))
    #if cached_path:
    #  self.__log("Found path to {} using route cache: {}".format(destinationID, cached_path))
    #  pkt = self.__make_packet_o(DSRMessageType.SEND, cached_path, originalPkt.contents, originalPkt.originatorID, originalPkt.originatorNodeID)
    #  pkt.originatorID = originalPkt.originatorID
    #  self.__network_sendto(pkt, int(cached_path[1]))
    #  self.__add_to_ack_buffer(pkt) #expect acknowledgement for send
    #else:

    #start route discovery
    temp = self.__make_packet_o(DSRMessageType.REQUEST, [self.ID], destinationID, originalPkt.originatorID, originalPkt.originatorNodeID)
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
        self.__log("Packet {} successfully acknowledged".format(ack[0].pretty_print()))
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

    #dont add self messages to route cache (this should never happen, but just in case)
    if int(a.fromID) != self.ID and len(a.path) > 1:
        #add new paths to route cache
        self.__route_cache.offer_route(a.path)

    #ignore messages that arent for us
    if int(a.toID) != self.ID and int(a.toID) != -1 :
      return

    #ignore self-self messages
    if int(a.fromID) == self.ID:
      return

    self.__receive_queue.append(a)
    self.__log("Receieved a packet {}".format(a.pretty_print()))

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
        self.__log("No acknowledgement received for packet {}. Dropping packet.".format(ack[0].pretty_print()))
        intpath = [int(value) for value in ack[0].path]
        next_index = intpath.index(self.ID)+1
        unreachable_node = ack[0].path[next_index]

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
          self.__log("No acknowledgement received for packet {}. Retransmitting...".format(msg.pretty_print()))
          #remove old record
          self.__awaiting_acknowledgement_buffer.remove(ack)
          #add to buffer again with updated transmissions
          toAdd.append((ack[0],time.time(),ack[2]+1))
    self.__awaiting_acknowledgement_buffer.extend(toAdd)

  #add a packet to the ack buffer
  #all the packets in this buffer are awaiting acknowledgement
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

  #check the send buffer for messages that need to be removed
  #or have their route discovery reinitiated
  def __check_send_buffer(self):
    for send in self.__send_buffer:
      end = time.time()
      elapsed = end - int(send[2])
      if send[3] > MAX_route_discoveries:
        self.__log("Dropping packet {}. No more route discoveries will be attempted.".format(send[1].pretty_print()))
        self.__send_buffer.remove(send)
      #exponential backoff
      elif elapsed > pow(MAX_time_between_request, send[3]):
        self.__log("Retrying route discovery for packet {} after {} seconds.".format(send[1].pretty_print(), elapsed))
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
        self.__debug_print("UNEXPECTED PACKET TYPE")
    for send in self.__send_queue:
      self.__route_discover(send[0], send[1])
    self.__receive_queue = []
    self.__send_queue = []

