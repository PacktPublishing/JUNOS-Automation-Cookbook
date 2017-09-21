#!/usr/bin/env python

import sys
import time

FILENAME = "/var/tmp/rules.txt"

rules = open(FILENAME).read().splitlines()
for r in rules:
        sys.stdout.write("announce flow route { match { " + r + ' } then { discard; } }\n')
        sys.stdout.flush()

while True:
        sys.stdin.read()
