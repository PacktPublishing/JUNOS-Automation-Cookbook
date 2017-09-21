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

cmdline = argparse.ArgumentParser(description="Python JUNOS PyEZ Client")
cmdline.add_argument("target", help="Target router to query")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=8443)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 60

config = dev.rpc.get_configuration(normalize=True)
ifd = 		config.xpath("interfaces/interface")
ifl = 		config.xpath("interfaces/interface/unit")
iflacli = 	config.xpath("interfaces/interface/unit/family/inet/filter/input")
iflaclo = 	config.xpath("interfaces/interface/unit/family/inet/filter/output")
vrrp = 		config.xpath("interfaces/interface/unit/family/inet/address/vrrp-group")
vrrpauth = 	config.xpath("interfaces/interface/unit/family/inet/address/vrrp-group/authentication-key")
vrf = 		config.xpath("routing-instances/instance[instance-type='vrf']")
ibgp = 		config.xpath("protocols/bgp//neighbor[type='internal' or ../type='internal']")
ebgp = 		config.xpath("protocols/bgp//neighbor[type='external' or ../type='external']")
bgpv = 		config.xpath("routing-instances/instance/protocols/bgp//neighbor")
bgpht =     config.xpath("//bgp//neighbor[hold-time<30 or ../hold-time<30]")
l2c =		config.xpath("protocols/l2circuit//virtual-circuit-id")

print "           Hostname:\t %s" % dev.facts['hostname']
print "              Model:\t %s" % dev.facts['model']
print "            Version:\t %s\n" % dev.facts['version']

print "Physical interfaces:\t %u" % len(ifd)
print " Logical interfaces:\t %u" % len(ifl)
print "     with input ACL:\t %u" % len(iflacli)
print "    with output ACL:\t %u" % len(iflaclo)
print "          with VRRP:\t %u" % len(vrrp)
print "     with VRRP/auth:\t %u" % len(vrrpauth)
print "        L2 circuits:\t %u" % len (l2c)
print "  Routing instances:\t %u" % len(vrf)
print "         IBGP peers:\t %u" % len(ibgp)
print "         EBGP peers:\t %u" % len(ebgp)
print "    L3VPN BGP peers:\t %u" % len(bgpv)
print "   BGP w/ HOLD < 30:\t %u" % len(bgpht)

dev.close()

# w200324:ch5 chappa10$ ./pyez-config-scan.py -p 8932 -u auto_script 127.0.0.1
#            Hostname:	 ber-alb-score-1-re0	Model:	 MX960

# Physical interfaces:	 119
#  Logical interfaces:	 892
#      with input ACL:	 29
#     with output ACL:	 19
#           with VRRP:	 783
#      with VRRP/auth:	 91
#         L2 circuits:	 11
#   Routing instances:	 602
#          IBGP peers:	 121
#          EBGP peers:	 0
#     L3VPN BGP peers:	 48
#    BGP w/ HOLD < 30:	 1


