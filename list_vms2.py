#!/usr/bin/env python

# Print out IP of guest VMs
#
# Adapted from ddu@redhat.com
# Adapted by feichashao@gmail.com
# 
# Python version 2.7
# 2016.Mar.25
#
# Tested in RHEL6 KVM environment.
#
# FIXME:
# 1. For the sake of time saving, this script only try to find SOME but NOT ALL ip addresses of each VM. Maybe we could come up with method to do it both time-saving and complete.


import subprocess
import xml.etree.ElementTree as ET
import os

#### Variables ####
# command to get runnng VMs.
list_vms = "virsh list | grep running | awk '{print $2}'"
subnet = "192.168.122.0/24"
# command to get arp table.
list_arp = "arp -an | sed 's/(//g' | sed 's/)//g' | grep -v incomplete | grep 192.168.122 | awk '{print $2,$4}'"
fping_cmd = 'fping -c1 -g ' + subnet + ' > /dev/null 2>&1'



#### Functions ####

# Get IP/MAC mapping from arp table. ip_mac_table = { mac : [ip]  }
def get_ip_mac_map ():
    ip_mac_table = {}
    arp_table = subprocess.Popen(list_arp, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()
    while arp_table:
        mac = arp_table.pop()
        ip = arp_table.pop()
        if mac in ip_mac_table:
            ip_mac_table[mac] = [ip]
        else:
            ip_mac_table[mac] += [ip]
    return ip_mac_table

# Get IP address of a VM(node).
# Return [IP1, IP2, IP3, ...]
def get_node_ip (node, ip_mac_table):
    ip_list = []
    try:
        filename = '/etc/libvirt/qemu/' + node + '.xml'
        tree = ET.parse(filename)
        for mac in tree.findall('./devices/interface/mac'):
            mac_address = mac.attrib['address']
            if mac_address in ip_mac_table:
                ip_list += ip_mac_table[mac_address]
    except IOError as ioerror:
        print "Fire error: " + str(ioerror)
    return ip_list

# Get running VMs.
# Retrun [ node1, node2, node3, ...]
def get_running_vms():
    return subprocess.Popen(list_vms, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()

# Refresh system arp table, this may take a few second.
def refresh_arp():
    os.system(fping_cmd)

# In RHEL/CentOS, virsh command need to be run by root.
if os.getuid() != 0:
    print "Only root can run this script. Exit."
    quit()

running_vms = get_running_vms()

left_vms = []
ip_mac_table = get_ip_mac_map()

print "Node\t IP"
for vm in running_vms:
    ips = get_node_ip(vm, ip_mac_table)
    if len(ips) > 0:
        print vm + "\t" + ', '.join(ips)
    else:
        left_vms.append(vm)

if len(left_vms) > 0:
    refresh_arp()
    ip_mac_table = get_ip_mac_map()
    for vm in left_vms:
        ips = get_node_ip(vm, ip_mac_table)
        print vm + "\t" + ', '.join(ips)
