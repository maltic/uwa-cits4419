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

from collections import defaultdict
import time

def millis():
  return int(round(time.time() * 1000))

class RouteCache:
  def __init__(self, myID):
    #graph representation
    self.__edge_list = defaultdict(set)
    #ages of all edges
    self.__edge_age = defaultdict(dict)
    #id of root node
    self.__me = myID
    #maximum age of a link in milliseconds
    self.__MAX_DELTA = 1000

  def offer_route(self, route):
    #attach the route information into the cache
    for i in range(len(route)-1):
      self.add_link(route[i], route[i+1])
    
  def add_link(self, fromID, toID):
    #adds a single link the cache
    t = millis()
    self.__edge_list[fromID].add(toID)
    self.__edge_list[toID].add(fromID)
    self.__edge_age[fromID][toID] = t
    self.__edge_age[toID][fromID] = t

  def remove_link(self, fromID, toID):
    #removes a given link from the cache
    self.__edge_list[fromID].discard(toID)
    self.__edge_list[toID].discard(fromID)
    del self.__edge_age[fromID][toID]
    del self.__edge_age[toID][fromID]
    
  def get_shortest_path(self, toID):
  
    #expire old links
    currT = millis()
    r = [] # things to delete
    for fromID in self.__edge_age.keys():
      for tID in self.__edge_age[fromID].keys():
        age = currT - self.__edge_age[fromID][tID]
        if age > self.__MAX_DELTA:
          r.append((fromID, tID))
          
    for a, b in r:
      del self.__edge_age[a][b]
      self.__edge_list[a].discard(b)
          
    #perform a simple bfs to find the SSSP
    q = []
    q.append(self.__me)
    visited = set()
    visited.add(self.__me)
    parent = dict() #keeping parents is faster than copying new lists
    while q:
      curr = q.pop(0)
      if curr == toID:
        break
      for child in self.__edge_list[curr]:
        if not (child in visited):
          parent[child] = curr
          q.append(child)
          visited.add(child)
    #follow parent ids to rebuild path
    if toID in parent:
      path = []
      curr = toID
      while curr != self.__me:
        path.append(curr)
        curr = parent[curr]
      return list(reversed(path))
    else:
      return None
      
      
    
    
if __name__ == '__main__':
  print("Just some testing, don't mind me...")
  rc = RouteCache(5)
  rc.offer_route([1,2,3,5,7,11])
  rc.offer_route([11,5,4,8,9])
  print("{}".format(rc.get_shortest_path(11)))
  rc.remove_link(5, 11)
  print("{}".format(rc.get_shortest_path(11)))
  print("{}".format(rc.get_shortest_path(9)))
  print("{}".format(rc.get_shortest_path(12)))
  time.sleep(1)
  rc.offer_route([4,5,2,12,55,32,2,3, 99,9])
  print("{}".format(rc.get_shortest_path(9)))
  print("{}".format(rc.get_shortest_path(3)))
