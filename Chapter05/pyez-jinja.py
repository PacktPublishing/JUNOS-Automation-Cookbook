#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
import struct
import socket
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError

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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ Config Template Tool")
cmdline.add_argument("-f", metavar="template", help="Template file to use", required=True)
cmdline.add_argument("-t", metavar="router", help="Target router to configure", required=True)
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())

cmdline.add_argument("--p2p", metavar="subnet", help="PE-CE subnet, A.B.C.D", required=True)
cmdline.add_argument("--ifd", metavar="interface", help="Physical interface", required=True)
cmdline.add_argument("--vlan", metavar="vlan", help="VLAN identifer", required=True)
cmdline.add_argument("--vrf", metavar="VRF", help="VRF identifier", required=True)

cmdline.add_argument("--cst", metavar="prefix/len", help="Prefix to statically route", action="append")

args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

p2p_pe = socket.inet_ntoa(struct.pack("!L",
	(struct.unpack("!L", socket.inet_aton(args.p2p))[0] & 0xfffffffd) + 1))
p2p_ce = socket.inet_ntoa(struct.pack("!L",
	(struct.unpack("!L", socket.inet_aton(args.p2p))[0] & 0xfffffffd) + 2))

dev = Device(host=args.t, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 120

with Config(dev, mode="private") as config:
	try:
		config.load(template_path=args.f, template_vars={
			'ifd': args.ifd,
			'vlan':args.vlan,
			'vrf': args.vrf,
			'p2p_pe': p2p_pe,
			'p2p_ce': p2p_ce,
			'cst': args.cst if args.cst!=None else []
		})
	except ConfigLoadError, e:
		if (e.rpc_error['severity']=='warning'):
			print "Warning: %s" % e.message
		else:
			raise

	diff = config.diff()
	if (diff!=None):
		print diff
	config.commit()

dev.close()




