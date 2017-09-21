#!/usr/bin/env python

import sys
import httplib
import ssl
import base64
import argparse
import getpass
import json
import os
import io

# Error handling
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = onError

cmdline = argparse.ArgumentParser(description="Python JUNOS REST Client")
cmdline.add_argument("target", help="Target router to query")
cmdline.add_argument("-t", choices=["xml", "json", "text"], help="Type of output", default="xml")
cmdline.add_argument("-r", metavar="rpc-call", help="RPC call to make", default="get-software-information")
cmdline.add_argument("-c", metavar="certificate", help="Router's self-signed certificate .pem file")
cmdline.add_argument("-p", metavar="port", help="TCP port", default=8443)
cmdline.add_argument("-u", metavar="username", help="Remote username", default=getpass.getuser())
args=cmdline.parse_args()

try:
    passwordFile = os.path.expanduser("~")+"/.pwaccess"
    if os.stat(passwordFile)[0]&63==0:
        passwords = json.load(io.open(passwordFile))
        password = passwords[args.u+"@"+args.target]
    else:
        sys.stderr.write("Warning: password file "+passwordFile+" must be user RW (0600) only!\n")
        sys.exit(1)

except Exception as e:
    print(e)
    password=getpass.getpass("Password: ")

basicAuthorization = base64.b64encode(args.u+":"+password)

context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=args.c)
context.check_hostname=False
if args.c==None:
    context.verify_mode=ssl.CERT_NONE

conn = httplib.HTTPSConnection(args.target, args.p, context=context)

headers = { 'Authorization' : 'Basic %s' %  basicAuthorization,
            'Accept': "text/xml" if args.t=="xml" else
            "application/json" if args.t=="json" else "text/plain" }

try:
    conn.request("GET", '/rpc/'+args.r, headers=headers)

except ssl.SSLError as e:
    sys.stderr.write("SSL error: "+str(e))
    sys.exit()

response = conn.getresponse()
responseData = response.read()

print response.status, httplib.responses[response.status]
if responseData:
    print responseData

if args.t=="json":
    data = json.loads(responseData)

    if 'software-information' in data:
        print "Software version: ", data['software-information'][0]['junos-version'][0]['data']



