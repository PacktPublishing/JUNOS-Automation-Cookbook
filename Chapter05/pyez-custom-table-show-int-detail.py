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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ show int detail (custom)")
cmdline.add_argument("target", help="Target router to query")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

# Load custom BGP table definition

interfaceYAML = """
---
InterfaceTable:
    rpc: get-interface-information
    args:
        detail: True
    item: logical-interface
    view: InterfaceView

InterfaceView:
    fields: 
        bytes_in: traffic-statistics/input-bytes
        bytes_out: traffic-statistics/output-bytes
        pkts_in: traffic-statistics/input-packets
        pkts_out: traffic-statistics/input-packets
"""


myModule = FactoryLoader().load(yaml.load(interfaceYAML))
globals().update(myModule)

dev = Device(host=args.target, user=args.u, port=args.p, password=password, gather_facts=False)
dev.open()
dev.timeout = 120

# peer_address incldudes +port number if there is a TCP socket there
ifls = InterfaceTable(dev).get("xe-7/2/3.1035")

print  "%12s\t%10s\t%10s\t%10s\t%10s" % ("Interface", "bytesIn", "bytesOut", "pktsIn", "pktsOut")
for ifl in ifls:

    print  "%12s\t%10s\t%10s\t%10s\t%10s" % (ifl.name, ifl.bytes_in, ifl.bytes_out, ifl.pkts_in, ifl.pkts_out)

dev.close()




