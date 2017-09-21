#!/usr/bin/env python

import sys
import argparse
import getpass
import os
import io
import email
import xml.etree.ElementTree as ET
import jxmlease
import urllib3
import requests
import re

def onError(exception_type, exception, traceback):
  sys.stderr.write("%s: %s\n" % (exception_type.__name__,   
                      exception))
#sys.excepthook = onError

MIME={
        "xml": "text/xml",
        "json": "application/json",
        "text": "text/plain"
}

def configRpc(config):
 return str.format((
    "<lock><target><candidate/></target></lock>\r\n"
    "<edit-config><target><candidate/></target><config>"
    "{config}</config></edit-config>\r\n"
    "<commit/>"
    "<unlock><target><candidate/></target></unlock>\r\n"
  ), config=config)


def getPassword():
  password=""
  try:
    passwordFile = os.path.expanduser("~")+"/.pwaccess"
    if os.stat(passwordFile)[0]&63==0:
      passwords = json.load(open(passwordFile))
      password = passwords[args.u+"@"+args.target]
    else:
      raise RuntimError("Warning: password file %s must be user RW 0600 only!" % passwordFile)

  except Exception as e:
    password=getpass.getpass("Password: ")

  return password

def decodePostResponse(response):
  print response.text
  response_parts=[]
  msg = email.message_from_string(
    "Content-Type: %s\r\n\r\n%s" %
   (response.headers['content-type'], response.text))

  for part in msg.walk():
    if (part.get_content_type()=="application/xml" or
       part.get_content_type()=="text/xml" or
       part.get_content_type()=="text/plain"):
         response_parts.append(part.get_payload(decode=True))

  if (len(response_parts)==0):
    raise RuntimeError("Unexpected empty POST response")

  try:
    lock=jxmlease.parse(response_parts[0])
    load=jxmlease.parse(response_parts[1])
    commit=jxmlease.parse(response_parts[2])

  except:
    raise RuntimeError("Malformed XML response:\n%s\n" %     
                   (response_parts[-1]))

  if ('ok' in lock and
    'load-success' in load and
    'commit-results' in commit):
      if not 'xnm:error' in commit['commit-results']:
        return "OK"
  else:
    return "FAIL"

cmdline = argparse.ArgumentParser(description="Python JUNOS REST Client")
cmdline.add_argument("target", help="Target router to query") 
cmdline.add_argument("-t", choices=["xml", "json", "text"],
                      help="Type of output", default="xml")
cmdline.add_argument("-c", metavar="certificate",
                      help="Router's self-signed certificate .pem file")
cmdline.add_argument("-p", metavar="port",
                      help="TCP port", default=8443)
cmdline.add_argument("-u", metavar="username",
                      help="Remote username",           
default=getpass.getuser())
cmdline.add_argument("-f", metavar="config", help="Configuration file to apply")
args=cmdline.parse_args()

if args.c==None:
  urllib3.disable_warnings()

config = open(args.f).read()

r = requests.post("https://"+args.target+":"+str(args.p)+"/rpc",
                   params={'stop-on-error': 1},
                   auth=(args.u, getPassword()),
                   headers = {
                      'Content-Type': "text/xml",
                      'Accept': MIME[args.t]
                  },
                  verify=args.c if args.c!=None else False,
                  data=configRpc(config),
                 )

if r.status_code==200:
  print decodePostResponse(r)
else:
  raise RuntimeError("Unexpected server response: %s %s" %   
  (str(r.status_code), r.reason))

