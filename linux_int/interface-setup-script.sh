#! /bin/bash

# TODO: add interface parametre arguments.

# set some parameters in /proc necessary for ad-hoc routing */
# enable ip forwarding */
sysctl -w net/ipv4/ip_forward=1

# disable sending and accepting of ICMP redirects */
sysctl -w net/ipv4/conf/all/accept_redirects=0
sysctl -w net/ipv4/conf/all/send_redirects=0

# enable min route delay
sysctl -w net/ipv4/route/min_delay=0

# ensure tunctl is installed
apt-get install uml-utilities
# add our tap interface
tunclt -t tap0
# bring new interface up
ifconfig tap0 up
# configure it
ifconfig tap0 127.0.0.2 netmask 255.255.255.255
# delete all existing default routes
ip route del 0/0
# add a new default route for the tap interface.
route add add default gw 127.0.0.2 tap0

#put wireless card in promiscuous mode
iwconfig eth1 mode monitor