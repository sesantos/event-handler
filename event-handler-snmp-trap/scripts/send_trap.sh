#!/bin/bash
#send_trap.sh public 10.144.200.252 linkDown ethernet-1/1 2 mgmt
index=$(sr_cli info from state interface $4 ifindex | grep ifindex | tr -dc '0-9')
sudo ip netns exec srbase-$6 snmptrap -v 2c -c $1 $2 '' IF-MIB::$3  ifIndex i $index ifAdminStatus i 1 ifOperStatus i $5
