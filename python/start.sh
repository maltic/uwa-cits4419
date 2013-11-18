#!/bin/bash

IP=`/sbin/ifconfig | grep -A 1 wlan0 | sed -n '2 p' | awk '{print $2}' | awk '{split($0,array,":")}{print array[2]}'`

python3 linux_network.py $IP
