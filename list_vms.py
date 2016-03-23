#!/usr/bin/env python
# This script will run well only if the arp cache is complete,
# which means the items in arp table  will not be deleted if 
# you did not touch the vm for a very long time.
# Also, this script suppose every vm only have one IP address,
# If you have more than one IP address on the vm, you will only
# get one IP address.

# script version:   0.1
# python version:   2.7

import subprocess
import xml.etree.ElementTree as ET
import os

# In RHEL, virsh commands need to be run by root.
if os.getuid() != 0:
    print "This script need to be run by user root!"
    quit()

print
print "\t======================================================="
print "\tPlease note that this script is only tested on RHEL6,"
print "\tif you want to use it in other versions of RHEL or other"
print "\tdistributions, you may need to customize it."
print "\t======================================================="
print

# get the running vms lists and save them into a list named running_vms
list_vms = "virsh list | grep running | awk '{print $2}'"
running_vms = subprocess.Popen(list_vms, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()

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
        mac_address = tree.find('./devices/interface/mac').attrib['address']
        try:
            for (ip,mac) in ip_mac_table.items():
                if mac == mac_address:
                    return ip
        except:
            print "Could not find IP Address assigned!!!"
            return None
    except IOError as ioerror:
        print "Fire error: ' + str(ioerror)"
        return None

print "\tCurrent running virtual machines are: "

for vm in running_vms:
    print "\t======\t",
    print vm,

    print "\t\t",
    print get_ip_address(vm),
    print "\t======"

print
