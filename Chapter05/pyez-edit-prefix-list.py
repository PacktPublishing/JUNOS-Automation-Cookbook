#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ Prefix List Tool")
cmdline.add_argument("-t", metavar="router", help="Target router to query", required=True)
cmdline.add_argument("-a", metavar="prefix/len", help="Prefix to add", action="append")
cmdline.add_argument("-d", metavar="prefix/len", help="Prefix to delete", action="append")
cmdline.add_argument("-l", metavar="prefix-list", help="prefix-list name", required=True)
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

if (args.a==None and args.d==None):
	print "Nothing to do!"
	sys.exit(1)

dev = Device(host=args.t, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 120

with Config(dev, mode="private") as config:
	if args.d!=None:
		for p in args.d:
			try:
				config.load("delete policy-options prefix-list %s %s" % (args.l, p), format="set")
			except ConfigLoadError, e:
				if (e.rpc_error['severity']=='warning'):
					print "Warning: %s" % e.message
				else:
					raise
	if args.a!=None:
		for p in args.a:
			try:
				config.load("set policy-options prefix-list %s %s" % (args.l, p), format="set")
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




