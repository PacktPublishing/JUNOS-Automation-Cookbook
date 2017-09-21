#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
from jnpr.junos import Device

# def getPass(target):
# 	try:
# 	    passwordFile = os.path.expanduser("~")+"/.pwaccess"
# 	    if os.stat(passwordFile)[0]&63==0:
# 	        passwords = json.load(io.open(passwordFile))
# 	        return(passwords[target])
# 	    else:
# 	        sys.stderr.write("Warning: password file "+passwordFile+" must be user RW (0600) only!\n")
# 	        sys.exit(1)

# 	except Exception as e:
# 	    return(getpass.getpass("Password: "))

# Error handling
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)
sys.excepthook = onError

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ Route lookup")
cmdline.add_argument("destination", help="Network destination to lookup")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=8443)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
cmdline.add_argument("-t", metavar="target", help="Target router to query", required=True)
cmdline.add_argument("-R", metavar="instance", help="Routing instance to use", default="")
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.t) if 'getPass' in globals() else ""

dev = Device(host=args.t,
			user=args.u,
			port=args.p,
			password=password)
dev.open()
print dev.timeout
dev.timeout = 60

result = dev.rpc.get_route_information(normalize=True, destination=args.destination, detail=True, table=args.R+".inet.0" if args.R!="" else "inet.0")

print "%s/%s" % (result.findtext("route-table/rt/rt-destination"), 
	result.findtext("route-table/rt/rt-prefix-length"))

for route in result.findall("route-table/rt/rt-entry"):
	protocol = route.findtext("protocol-name")
	task = route.findtext("task-name")
	age = route.findtext("age")
	active = len(route.findall("current-active"))
	info = ""
	if protocol=="BGP":
		info+="NEXT_HOP "+route.findtext("gateway")+" LOCAL_PREF "+route.findtext("local-preference")+" AS_PATH "+route.findtext("as-path")
	print "%c\t%s (%s) %s" % ("*" if active==1 else " ", task if protocol=="BGP" else protocol, age, info)

	nexthops = route.xpath("nh")
	for nh in nexthops:
		selected = len(nh.xpath("selected-next-hop"))
		to = nh.findtext("to")
		via = nh.findtext("via")
		print "\t\t\t\t%c%s %s %s" % (">" if selected==1 else " ", to if to!=None else "", "via" if via!=None else "", via)

dev.close()


