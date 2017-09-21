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
    sys.stderr.write("%s: %s\n" % (exception_type.__name__, exception))
sys.excepthook = onError

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ ISIS Database Extraction Tool")
cmdline.add_argument("target", metavar="target", help="Target router to query")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 60
result = dev.rpc.get_isis_database_information(normalize=True, detail=True)

graph={'nodes': [], 'links': []}
for entry in result.xpath("isis-database[level='2']/isis-database-entry"):
	lspid = entry.findtext("lsp-id")
	node=lspid[:-3]
	if not node.endswith(".00"):
		node="_"+node;
	if not node in graph['nodes']:
		graph['nodes'].append(node)
	for neighbor in entry.xpath("isis-neighbor"):
		neighborid = neighbor.findtext("is-neighbor-id")
		metric = neighbor.findtext("metric")
		topology = neighbor.findtext("isis-topology-id")
		if topology=="" or topology=="IPV4 Unicast":
			if not neighborid.endswith(".00"):
				neighborid="_"+neighborid;
			if not neighborid in graph['nodes']:
				graph['nodes'].append(neighborid)
			graph['links'].append([node, neighborid, metric])

dev.close()

print repr(json.dumps(graph))
