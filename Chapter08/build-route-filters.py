#!/usr/bin/env python

import sys
import io
import getpass
import os
import json
import argparse
import subprocess
import tempfile
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import RpcError
# from lxml import etree

SUFFIX=".auto"
IRRTOOL="bgpq3"
MAX_PREFIXES=5000
MAX_DELS=10

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

cmdline = argparse.ArgumentParser(description="Python JUNOS BGP Prefix-list build tool")
cmdline.add_argument("target", metavar="router", help="Target router to analyse/configure")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=830)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
cmdline.add_argument("-f", metavar="resource", help="Dismiss configuration change size concerns for resource", action="append", default=[])
args=cmdline.parse_args()

password=getPass(args.u+"@"+args.target) if 'getPass' in globals() else ""

dev = Device(host=args.target, user=args.u, port=args.p, password=password)
dev.open()
dev.timeout = 120

configuration = dev.rpc.get_config(filter_xml='<policy-options></policy-options>')

for name in configuration.xpath("policy-options/prefix-list/name"):
	if name.text.endswith(SUFFIX):
		sys.stdout.write("Checking prefix list: %s\n" % (name.text))

		try:
			with tempfile.NamedTemporaryFile() as file:
				subprocess.check_call([IRRTOOL, '-J', '-S', 'RIPE', ("-l %s"%name.text), name.text[:-len(SUFFIX)]], stdout=file)
				prefix_count = len(open(file.name).read().splitlines())
				if (prefix_count>MAX_PREFIXES):
					sys.stdout.write("Skipping %s: too many prefixes (%d>%d)\n" % (name.text, prefix_count, MAX_PREFIXES))
				else:

					try:
						with Config(dev, mode="private") as config:
							config.load(path=file.name, format="text")
							diff = config.diff()
							if (diff!=None):
								adds=0
								dels=0
								for line in diff.splitlines():
									if line.startswith("+"):
										adds+=1
									if line.startswith("-"):
										dels+=1
								sys.stdout.write(diff)
								if (dels>MAX_DELS and not name.text in args.f):
									sys.stdout.write("%s: %d addition(s), %d deletion(s): too many deletions - skipping\n" % (name.text, adds, dels))
								else:
									sys.stdout.write("%s: %d addition(s), %d deletion(s): committing\n" % (name.text, adds, dels))
									config.commit(comment="Automatic prefix-filter update for %s" % name.text)

							else:
								sys.stdout.write("No work to do for %s\n" % (name.text))


					except RpcError, e:
						sys.stderr.write("Error occurred while trying to configure %s: %s\n" % (name.text, e.message))

		except subprocess.CalledProcessError, e:
			print e
			sys.stderr.write("Failed to run %s: return code %d\n" % IRRTOOL, e.returncode)

dev.close()