import sys
import struct
import random
import binascii
import functools

from . import subsetxor
from . import crc_catalog

def solve(data, unknowns, desired, crcfunc):
	zeroed = [0]*len(data)
	csum_nulls = crcfunc(bytes(zeroed))

	# calculate subsetxor target
	emptied = list(data)
	for position in unknowns:
		bit = 1<<(7-position%8)
		emptied[position//8] &= ~bit
	csum_emptied = crcfunc(bytes(emptied))
	target = csum_emptied ^ desired

	# calculate subsetxor inputs
	inputs = []
	for position in unknowns:
		bit = 1<<(7-position%8)
		# set bit
		zeroed[position//8] |= bit

		csum = crcfunc(bytes(zeroed))
		inputs.append(csum_nulls ^ csum)

		# clear bit
		zeroed[position//8] ^= bit

	# solve subsetxor
	selector = subsetxor.solve(inputs, target)
	if selector == []:
		return None

	# set the results on the data, return it
	result = emptied
	for i in range(len(selector)):
		if not selector[i]:
			continue
		position = unknowns[i]
		bit = 1<<(7-position%8)
		result[position//8] |= bit

	return bytes(result)

def reflect(x, width):
	y = 0
	for i in range(width):
		y <<= 1
		y |= (x & 1)
		x >>= 1
	return y

def compute(data, crc_name):
	entry = [e for e in crc_catalog.database if e['name']==crc_name][0]
	if not entry:
		raise Exception('unrecognized algorithm: %s' % crc_name)

	poly = entry['poly']
	checksum = entry['init']
	width = entry['width']
	msb_mask = 1<<(width-1)

	for b in data:
		if entry['refin']:
			b = reflect(b, 8)

		checksum = checksum ^ (b << (width-8))

		for k in range(8):
			if checksum & msb_mask:
				checksum = ((checksum ^ msb_mask) << 1) ^ poly
			else:
				checksum = checksum << 1

	checksum ^= entry['xorout']

	if entry['refout']:
		checksum = reflect(checksum, 64)

	return checksum
