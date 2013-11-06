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

#DSR Message Type
class DSRMessageType:
  REQUEST = 1
  REPLY = 2
  ERROR = 3
  SEND = 4
  ACK = 5

#DSR Packet
class Packet:
  def __init__(self):
    #work out what these are by parsing packet
    self.type = 0
    self.path = []
    self.contents = ""
    self.id = -1
    self.fromID = -1
    self.originatorID = -1
    self.toID = -1

  #prints out information of this packet
  def __str__(self):
    out = [self.type, ">".join(str(x) for x in self.path), self.contents, self.id, self.fromID, self.originatorID, self.toID]
    return "|".join(str(x) for x in out)

  def __repr__(self):
    return self.__str__()

  #works like a constructor
  #parses a network string into a packet object
  def from_str(packetStr):
    pkt = Packet()
    toks = packetStr.split("|")
    pkt.type = int(toks[0])
    pkt.path = toks[1].split(">")
    pkt.contents = toks[2]
    pkt.id = int(toks[3])
    pkt.fromID = int(toks[4])
    pkt.originatorID = int(toks[5])
    pkt.toID = int(toks[6])
    return pkt
