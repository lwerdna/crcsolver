import sys
import struct
import random
import binascii
import functools

from . import subsetxor

def bitstr_int(val, width):
	return bin(val)[2:].rjust(width, '0')

def bitstr(data):
	return ''.join([bitstr_int(val,8) for val in data])

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

		#print('crc(%s) == %s' % (bytes(zeroed), bitstr_int(csum,16)))
		# clear bit
		zeroed[position//8] ^= bit

	# solve subsetxor
	selector = subsetxor.solve(inputs, target)

	# set the results on the data, return it
	result = emptied
	for i in range(len(selector)):
		if not selector[i]:
			continue
		position = unknowns[i]
		bit = 1<<(7-position%8)
		result[position//8] |= bit

	return bytes(result)

