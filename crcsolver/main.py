import sys
import struct
import random
import binascii
import functools

from . import subsetxor
from . import crc_catalog

def solve(data, unknowns, desired, crc_func):
	# crc_func can be a function or a name from the crc_catalog
	if type(crc_func) == str:
		crc_name = crc_func
		crc_func = lambda x: compute(x, crc_name)

	zeroed = [0]*len(data)
	csum_nulls = crc_func(bytes(zeroed))

	# calculate subsetxor target
	emptied = list(data)
	for position in unknowns:
		bit = 1<<(7-position%8)
		emptied[position//8] &= ~bit
	csum_emptied = crc_func(bytes(emptied))
	target = csum_emptied ^ desired

	# calculate subsetxor inputs
	inputs = []
	for position in unknowns:
		bit = 1<<(7-position%8)
		# set bit
		zeroed[position//8] |= bit

		csum = crc_func(bytes(zeroed))
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

def bit_gen(data, msb_first):
	for b in data:
		if not msb_first:
			b = reflect(b, 8)

		for i in range(8):
			yield b & 1
			b >>= 1

def compute(data, crc_name):
	if type(crc_name) == str:
		entry = [e for e in crc_catalog.database if e['name']==crc_name]
		if not entry:
			raise Exception('unrecognized algorithm: %s' % crc_name)
		entry = entry[0]
	else:
		entry = crc_name

	poly = entry['poly']
	checksum = entry['init']
	width = entry['width']
	msb_mask = 1<<(width-1)

	bg = bit_gen(data, entry['refin'])

	for bit in bg:
		checksum = checksum ^ (bit << (width-1))

		if checksum & msb_mask:
			checksum = ((checksum ^ msb_mask) << 1) ^ poly
		else:
			checksum = checksum << 1

	checksum ^= entry['xorout']

	if entry['refout']:
		checksum = reflect(checksum, width)

	return checksum
