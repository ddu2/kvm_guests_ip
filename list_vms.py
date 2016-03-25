#!/usr/bin/env python
#
# version:   0.3
# python :   2.7
# 
# data: 2016-03-25
#

import subprocess
import xml.etree.ElementTree as ET
import os

# In RHEL/CentOS, virsh command need to be run by root.
if os.getuid() != 0:
    print "This script need to be run by user root!"
    quit()

# get the running vms lists and save them into a list named running_vms
list_vms = "virsh list | grep running | awk '{print $2}'"
running_vms = subprocess.Popen(list_vms, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()

# get the ip and mac address map
list_arp = "arp -an | sed 's/(//g' | sed 's/)//g' | grep -v incomplete | grep 192.168.122 | awk '{print $4,$2}'"
def get_ip_mac_table():
    arp_table = subprocess.Popen(list_arp, shell=True, stdout=subprocess.PIPE).stdout.read().strip().split()
    ip_mac_table = {}
    while arp_table:
        mac = arp_table.pop(0)
        ip = arp_table.pop(0)
        if not ip_mac_table.get(mac,None):  
            ip_mac_table[mac] = [ip]
        else:
            ip_mac_table[mac].append(ip)
    return ip_mac_table

# get the ip address of a vm
def get_ip_address(node):
    ip_list = []
    try:
        filename = '/etc/libvirt/qemu/' + node + '.xml'
        tree = ET.parse(filename)
        for mac in tree.findall('./devices/interface/mac'):
            if mac.attrib['address'] in ip_mac_table:
                ip_list += ip_mac_table[mac.attrib['address']]
    except IOError as ioerror:
        print "Fire error: " + str(ioerror)
    return ip_list

# refresh arp table by fping command
def refresh_arp():
    os.system('fping -c1 -g 192.168.122.0/24 > /dev/null 2>&1')

ip_mac_table = get_ip_mac_table()

print "===== Host ===\t\t\t=== IP ==="
for vm in running_vms:
    print "===== " + vm,
    ips = get_ip_address(vm)
    if not len(ips):
        refresh_arp()
        ip_mac_table = get_ip_mac_table()
        ips = get_ip_address(vm)
    print "\t\t" + ' '.join(get_ip_address(vm))

print
