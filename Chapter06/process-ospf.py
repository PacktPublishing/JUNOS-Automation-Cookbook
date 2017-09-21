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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ OSPF Database Extraction Tool")
cmdline.add_argument("target", metavar="target", help="Target router to query")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 60
result = dev.rpc.get_ospf_database_information(normalize=True, detail=True)

graph={'nodes': [], 'links': []}

for entry in result.xpath("ospf-database[../ospf-area-header/ospf-area='0.0.0.0']"):
	lsaid = entry.findtext("lsa-id")
	lsatype = entry.findtext("lsa-type")
	if (lsatype=="Router"):
		graph['nodes'].append(lsaid)
		for link in entry.xpath("ospf-router-lsa/ospf-link"):
			linkid=link.findtext("link-id")
			linktype=link.findtext("link-type-name")
			metric=link.findtext("metric")

			if (linktype=="PointToPoint"):
				graph['links'].append([lsaid, linkid, metric])
			if (linktype=="Transit"):
				graph['links'].append([lsaid, "_"+linkid, metric])

dev.close()

print repr(json.dumps(graph))
