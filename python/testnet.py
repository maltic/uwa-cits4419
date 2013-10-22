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

import dsr

class TestNet:
  def __init__(self):
    self.dsr1 = dsr.DSR(self, 1)
    self.dsr2 = dsr.DSR(self, 2)
    self.dsr3 = dsr.DSR(self, 3)
  def send(self, msg, addr):
    self.dsr1.receive_packet(msg)
    self.dsr2.receive_packet(msg)
    self.dsr3.receive_packet(msg)
  def runSim(self):
    self.dsr1.send_message("test packet", 2)
    while True:
      self.dsr1.update()
      self.dsr2.update()
      self.dsr3.update()
      msgs = self.dsr2.pop_messages()
      if msgs != []:
        print("Messages receied by dsr2 : {} path was {}".format(msgs[0].contents, msgs[0].path))
        
if __name__ == '__main__':
  tn = TestNet()
  tn.runSim()
      
     
    
  
  
