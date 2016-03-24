#!/usr/bin/env python
# This script will run well only if the arp cache is complete,
# which means the items in arp table  will not be deleted if 
# you did not touch the vm for a very long time.
# Also, this script suppose every vm only have one IP address,
# If you have more than one IP address on the vm, you will only
# get one IP address.

# script version:   0.2
# python version:   2.7

import subprocess
import xml.etree.ElementTree as ET
import os

# In RHEL/CentOS, virsh command need to be run by root.
if os.getuid() != 0:
    print "This script need to be run by user root!"
    quit()

print
print "\t======================================================="
print "\tPlease note that this script only has been tested on RHEL6,"
print "\tif you want to use it in other versions of RHEL or other"
print "\tdistributions, you may need to customize it."
print "\t======================================================="
print

# get the running vms lists and save them into a list named running_vms
list_vms = "virsh list | grep running | awk '{print $2}'"
running_vms = subprocess.Popen(list_vms, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()

# use fping command to ping the network
print "\tScanning local subnet 192.168.122.0/24 ............"
os.system('fping -c1 -g 192.168.122.0/24 > /dev/null 2>&1')
print

# get the ip and mac map and save them into a list named arp_table
list_arp = "arp -an | sed 's/(//g' | sed 's/)//g' | grep -v incomplete | grep 192.168.122 | awk '{print $2,$4}'"
arp_table = subprocess.Popen(list_arp, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()

# create a dictionary and save the ip/mac pairs to it.
ip_mac_table = dict()
while arp_table:
    a = arp_table.pop(0)
    ip_mac_table[a] = arp_table.pop(0)

# get the ip address of a vm
def get_ip_address(node):
    try:
        filename = '/etc/libvirt/qemu/' + node + '.xml'
        tree = ET.parse(filename)
        for mac in tree.findall('./devices/interface/mac'):
            mac_address = mac.attrib['address']
            try:
                for (ip,mac_addr) in ip_mac_table.items():
                    if mac_addr == mac_address:
                        print ip, 
            except:
                print "Could not find IP Address assigned!!!"
    except IOError as ioerror:
        print "Fire error: " + str(ioerror)

print "\tCurrent running virtual machines are: "

for vm in running_vms:
    print "\t======",
    print vm,

    print "======:\n\t\t",
    get_ip_address(vm)
    print "\n"

print
