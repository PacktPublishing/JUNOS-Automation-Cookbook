#!/usr/bin/env python

from pprint import pprint
from jnpr.junos import Device
import getpass
import os
import json

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

target="10.0.201.201"
user="auto"
password=getPass(user+"@"+target)

dev = Device(host=target, user=user, password=password)
dev.open()

pprint(dev.facts)

dev.close()


