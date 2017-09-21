#!/usr/bin/env python

import sys
import argparse
import os
import io
from string import Template

# Error handling
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)
sys.excepthook = onError

cmdline = argparse.ArgumentParser(description="Python Graph processor")
cmdline.add_argument("graph", help="JSON file describing graph")
cmdline.add_argument("-t", metavar="template", help="Template file", default="graph.html.template")
cmdline.add_argument("-o", metavar="output filename", help="File to output completed HTML", default="graph.html")
args=cmdline.parse_args()

jsonGraph = open(args.graph).read()
template = Template(open(args.t).read())

open(args.o, "w").write(template.substitute(graph=jsonGraph))
