#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
import struct
import socket
import io
from jnpr.junos import Device
from lxml import etree

def getPass(target):
	try:
		passwordFile = os.path.expanduser("~")+"/.pwaccess"
		if os.stat(passwordFile)[0]&63==0:
			passwords = json.load(io.open(passwordFile))
			return(passwords[target])
		else:
			sys.stderr.write("Warning: password file "+passwordFile+" must be user RW (0600) only!\n")
			sys.exit(1)
	except Exception as e:
		return(getpass.getpass("Password: "))

# Error handling
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)
sys.excepthook = onError

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ MPLS VPN Extraction Tool")
cmdline.add_argument("target", metavar="target", help="Target router to query")
cmdline.add_argument("community", metavar="community", help="target:NNN:NNN")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 60
result = dev.rpc.get_route_information(normalize=True, detail=True, table="bgp.l3vpn.0", community=args.community)

graph={'nodes': [], 'links': []}
graph['nodes'].append(args.community)

for route in result.xpath("route-table/rt"):
	destination = route.findtext("rt-destination")
	if not destination in graph['nodes']:
		graph['nodes'].append(destination)
	for entry in route.xpath("rt-entry"):
		nh = entry.findtext("protocol-nh/to")
		if not nh in graph['nodes']:
			graph['nodes'].append(nh)
			graph['links'].append([args.community, nh, 10])
		graph['links'].append([nh, destination, 10])


dev.close()

print repr(json.dumps(graph))
