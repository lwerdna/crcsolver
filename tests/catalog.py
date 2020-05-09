#!/usr/bin/env python3

# test everything in the crc catalog

import sys

from crcsolver import compute, solve
from crcsolver.crc_catalog import database

for entry in database:
	name = entry['name']
	print('testing %s forward' % name)
	actual = compute(b'123456789', name)
	expected = entry['check']

	if actual != expected:
		print('  actual: 0x%X' % actual)
		print('expected: 0x%X' % expected)
		sys.exit(-1)

	print('testing %s reverse' % name)

	tmp = solve(b'_23456789', range(8), actual, name)
	assert compute(tmp, name) == actual

	tmp = solve(b'1_3456789', range(8,16), actual, name)
	assert compute(tmp, entry) == actual

	tmp = solve(b'12_456789', range(16,24), actual, name)
	assert compute(tmp, entry) == actual

print('PASS')
sys.exit(0)

