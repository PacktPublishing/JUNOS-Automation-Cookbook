#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
import yaml

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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ BGP Tool (custom)")
cmdline.add_argument("target", help="Target router to query")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

# Load custom BGP table definition

bgpYAML = """
---
BgpTable:
    rpc: get-bgp-summary-information
    key: peer-address
    item: bgp-peer
    view: BgpView

BgpView:
    fields: 
        asn: peer-as
        address: peer-address
        state: peer-state
        routes_accepted: bgp-rib/accepted-prefix-count
        routes_received: bgp-rib/received-prefix-count
        output_msgs: output-messages
        input_msgs: input-messages
        out_q: route-queue-count
"""


myModule = FactoryLoader().load(yaml.load(bgpYAML))
globals().update(myModule)

dev = Device(host=args.target, user=args.u, port=args.p, password=password, gather_facts=False)
dev.open()
dev.timeout = 60

# peer_address incldudes +port number if there is a TCP socket there
peers = BgpTable(dev).get()

print  "%20s\t%10s\t%10s\t%10s\t%s\t%s" % ("Peer", "ASN", "InMsgs", "OutMsgs", "OutQ", "State/PfxRcvd")
for peer in peers:
	routes_received = reduce(lambda x, y: int(x)+int(y), peer.routes_received) if type(peer.routes_received)==list else peer.routes_received
	routes_accepted = reduce(lambda x, y: int(x)+int(y), peer.routes_accepted) if type(peer.routes_accepted)==list else peer.routes_accepted

	print "%20s\t%10s\t%10s\t%10s\t%s\t%s" % (peer.address.split("+")[0],
							peer.asn,
							peer.input_msgs,
							peer.output_msgs,
							peer.out_q,
							str(routes_accepted)+"/"+str(routes_received) if (peer.state=="Established") else peer.state)	

dev.close()




