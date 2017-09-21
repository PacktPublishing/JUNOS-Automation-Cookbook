#!/usr/bin/env python

import sys
import getpass
import os
import json
import argparse
from jnpr.junos import Device
from lxml import etree

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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ Command Line Tool")
cmdline.add_argument("target", help="Target router to query")
cmdline.add_argument("command", help="Command line to run")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 60

rpc = dev.display_xml_rpc(args.command)

if type(rpc) is etree._Element:
	rpc.attrib['format']='text'
	result = dev.rpc(rpc)
	print result.text

else:
	print "XML RPC for command not available: ", rpc

dev.close()




