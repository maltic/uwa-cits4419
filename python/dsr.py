#Need to consider exponential back off limit for initiating new route discoveries
#Keep broken routes in cache for certain time? So that broken link request wont be forwarded
#How long to keep cached routes for?
#Shortening of routes by gratious reply?
#Piggyback route error msgs on a node's new route request.


import network

class DSRMessageType:
  REQUEST = 1
  REPLY = 2
  ERROR = 3
  SEND = 4
  ERROR = 5
  ACK = 6

next_packet_id = 0
msg_id = 0

class Packet:
  def __init__(self):
    #work out what these are by parsing packet
    self.type = ""
    self.path = []
    self.contents = ""
    self.id = -1
    self.fromID = -1
    self.msgID = -1

class RouteCache:
  def __init(self, myID):
    self.__edge_list = [[]]
    self.__me = myID

  def offer_route(self, route):
    #attach the route information into the cache
    #should also add the reverse route
    return

  def remove_link(self, link):
    #removes a given link from the cache
    return

  def get_path(self, toID):
    #first expires any old routes, then...
    #gets a route to the id specified
    return []
    

#works like a constructor
#make a packet out of some arguments
def make_packet(type, path, contents, msgID):
  pkt = Packet()
  pkt.type = type
  pkt.path = path
  pkt.contents = contents
  pkt.msgID = msgID
  return pkt
  
#works like a constructor  
#parses a network string into a packet object
def parse_packet(packetStr):
  pkt = Packet()
  return pkt


class DSR:
  def __init__(self):
    self.__receive_queue = []
    self.__send_queue = []
    self.__send_buffer = []
    self.__done_buffer = []
    self.__awaiting_acknowledgement_buffer = []
    self.ID = ""
    self.__route_cache = RouteCache(self.ID)

  def __network_broadcast(pkt):
    pkt.id = next_packet_id
    next_packet_id += 1
    pkt.fromID = self.ID
    #need to work out how to use the network layer
    return

  def __network_sendto(pkt, toID):
    pkt.id = next_packet_id
    next_packet_id += 1
    pkt.fromID = self.ID
    self.__awaiting_acknowledgement_buffer.append(pkt)
    #need to work out how to use the network layer
    return

  def __route_request(self, msg):
    if msg.contents == self.ID:
      msg.path.append(self.ID)
      rev_path = reversed(msg.path)
      next_index = rev_path.index(self.ID)+1
      __network_sendto(make_packet(DSRMessageType.REPLY, rev_path, msg.path[0], msg.msgID), rev_path[next_index])
    else:
      msg.path.append(self.ID)
      __network_broadcast(make_packet(DSRMessageType.REQUEST, msg.path, msg.contents, msg.msgID))

  def __route_reply(self, msg):
    #if i am the originator of the message then remove it from the send buffer
    #if not, then send it to the next guy on the list
    if msg.contents == self.ID:
      rev_path = reversed(msg.path)
      next_index = rev_path.index(self.ID)+1
      contents = self.__remove_from_send_buffer(msg.msgID)
      __network_sendto(make_packet(DSRMessageType.SEND, rev_path, contents, msg_id), rev_path[next_index])
      msg_id += 1
    else:
      next_index = msg.path.index(self.ID)+1
      __network_sendto(make_packet(DSRMessageType.REPLY, msg.path, msg.contents, msg.msgID), msg.path[next_index])
    #need to start route discovery if a link is broken
    #i havn't added this yet because I am not sure how the network layer will let us know

  def __route_error(self, msg):
    if msg.path[-1] == self.ID:
    #msg.contents should be the broken link
    #remove the broken link from route cache
      _network_broadcast(make_packet(DSRMessageType.ERR0R, msg.path, msg.contents, msg.msgID))
    else:
    #remove broken link
    #here should be just forwarding the error msg
      _network_broadcast(make_packet(DSRMessageType.ERR0R, msg.path, msg.contents, msg.msgID))
      
    #not implemented yet, because there is not route cache

  def __route_send(self, msg):
    #if I am the recipient, yay! add it to the done_buffer
    #if not, send it to the next guy on the list

    from_index = msg.path.index(self.ID)-1
    __network_sendto(make_packet(DSRMessageType.ACK, msg.path, self.ID, msg.msgID), msg.path[from_index])

    if msg.path[-1] == self.ID:
      self.__done_buffer.append(msg)
    else:
      next_index = msg.path.index(self.ID)+1
      __network_sendto(make_packet(DSRMessageType.SEND, msg.path, msg.contents, msg.msgID), msg.path[next_index])
    #need to start route discovery if a link is broken

  def __route_discover(self, msg, toID):
    #lookup route cache not implemented

    #start route discovery
    self.__send_buffer.append((msg,msg_id))
    self.__network_broadcast(make_packet(DSRMessageType.REQUEST, [self.ID], toID, msg_id))
    msg_id += 1

  def __msg_acknowledgement(msg):
    for ack in self.__awaiting_acknowledgement_buffer:
      if ack.id == msg.id:
        self.__awaiting_acknowledgement_buffer.remove(ack)
        return

  def receive_packet(self, pkt):
    self.__receive_queue.append(parse_packet(pkt))


  def send_message(self, contents, toID):
    self.__send_queue.append((contents, toID))

  def pop_messages(self):
    tmp = self.__done_buffer
    self.__done_buffer = []
    return tmp

  def __remove_from_send_buffer(self, ID):
    for send in self.__send_buffer:
      if (send[1] == ID):
        msg = send[0]
        self.__send_buffer.remove(send)
        return msg

  def update(self):
    for msg in self.__receive_queue:
      #send acknowledgement message back
      if msg.fromID != -1: #-1 fromID means broadcast
        self.__network_sendto(make_packet(DSRMessageType.ACK, [], "", msg.fromID))
      if msg.type == DSRMessageType.REQUEST:
        self.__route_request(msg)
      elif msg.type == DSRMessageType.REPLY:
        self.__route_reply(msg)
      elif msg.type == DSRMessageType.ERROR:
        self.__route_error(msg)
      elif self.type == DSRMessageType.SEND:
        self.__route_send(msg)
      elif self.type == DSRMessageType.ACK:
        self.__msg_acknowledgement(msg)
    for send in self.__send_queue:
      self.__route_discover(send)
    self.__receive_queue = []
    self.__send_queue = []
    #need to add exponential backoff from acknoledgement messages and error propagation
    