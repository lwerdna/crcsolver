#!/usr/bin/env python3

# test everything in the crc catalog

import sys

from crcsolver import compute
from crcsolver.crc_catalog import database

for entry in database:
	if entry['width'] % 8:
		continue

	name = entry['name']
	print('testing %s' % name)
	actual = compute(b'123456789', name)
	expected = entry['check']

	if actual != expected:
		print('  actual: 0x%X' % actual)
		print('expected: 0x%X' % expected)
		sys.exit(-1)

print('PASS')
sys.exit(0)

