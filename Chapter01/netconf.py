#!/usr/bin/env python

import sys
import subprocess
import xml.etree.ElementTree as ET

class NETCONFClient(object):

	DELIMITER = ']]>]]>\n'

	def __init__(self, hostname):
		self.ssh = subprocess.Popen([
				"/usr/bin/ssh",
				"-q",
				"-i", "junos_auto_id_rsa",
				"-p", "830",
				"-s", 
				hostname,
				"netconf",
			],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE)

	def __del__(self):
		self.ssh.stdin.close()

	def read(self):
		data=""
		for line in iter(self.ssh.stdout.readline, NETCONFClient.DELIMITER):
			if line=='':
				raise IOError("ssh session ended unexpectedly")
			data += line

		return ET.fromstring(data)

	def cmdrpc(self, cmd):
		e = ET.Element("rpc")
		e.append(ET.Element("command", {'format': "text"}))
		e.find("command").text = cmd;
		self.ssh.stdin.write(ET.tostring(e))
		self.ssh.stdin.write(NETCONFClient.DELIMITER)

# Error handling
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = onError

# Read command line
if len(sys.argv) < 3:
	print "Usage: netconf.py hostname command"
	sys.exit(1)

netconf = NETCONFClient("auto@"+str(sys.argv[1]))
response = netconf.read()
netconf.cmdrpc(" ".join(sys.argv[2:]))
response = netconf.read()

output = response.find(".//{urn:ietf:params:xml:ns:netconf:base:1.0}output")
config = response.find(".//{urn:ietf:params:xml:ns:netconf:base:1.0}configuration-output")
error = response.find(".//{urn:ietf:params:xml:ns:netconf:base:1.0}error-message")

if output != None:
	print output.text
elif config != None:
	print config.text
elif error != None:
	print error.text
else:
	print "NETCONF server provided no usable response"
