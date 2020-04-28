#!/usr/bin/env python3

import sys
import struct
import random
import binascii
import functools

import subsetxor

def bitstr_int(val, width):
	return bin(val)[2:].rjust(width, '0')

def bitstr(data):
	return ''.join([bitstr_int(val,8) for val in data])

def solve_hqx(data, unknowns, desired):
	# calculate subsetxor target
	cleared = list(data)
	for position in unknowns:
		bit = 1<<(7-position%8)
		cleared[position//8] &= ~bit
	csum_emptied = binascii.crc_hqx(bytes(cleared), 0)
	target = csum_emptied ^ desired
	
	# calculate subsetxor inputs
	zeroed = [0]*len(data)
	inputs = []
	for position in unknowns:
		bit = 1<<(7-position%8)
		zeroed[position//8] |= bit
		csum = binascii.crc_hqx(bytes(zeroed), 0)
		inputs.append(csum)
		#print('crc(%s) == %s' % (bytes(zeroed), bitstr_int(csum,16)))
		zeroed[position//8] ^= bit

	# solve subsetxor
	selector = subsetxor.solve(inputs, target)

	# set the results on the data, return it
	for i in range(len(selector)):
		if not selector[i]:
			continue
		position = unknowns[i]
		bit = 1<<(7-position%8)
		cleared[position//8] |= bit

	return bytes(cleared)	

if __name__ == '__main__':
	def crc_hqx_uint32_t(x):
		return binascii.crc_hqx(struct.pack('>I', x), 0)
	def crc_hqx_bytes(x):
		return binascii.crc_hqx(x, 0)
	def findnulls(x):
		lol = [list(range(8*i,8*i+8)) for (i,byte) in enumerate(x) if byte==0]
		return functools.reduce(lambda a,b:a+b, lol, [])

	assert solve_hqx(b'testes1\x00', range(56,64), 0x2E5A) == b'testes12'
	assert solve_hqx(b'testes\x002', range(48,56), 0x2E5A) == b'testes12'

	input = b'bl\x00z\x00a\x00d'
	recovered = solve_hqx(input, findnulls(input), 0x6B21)
	assert crc_hqx_bytes(recovered) == 0x6B21

	crc = crc_hqx_uint32_t
	for i in range(10000):
		# generate random 32-bit input, calculate its crc
		data_int = random.getrandbits(32)
		data = struct.pack('>I', data_int)
		csum_orig = crc(data_int)
		print('crc_a(0x%X) = %s' % (data_int, bitstr_int(csum_orig,16)))

		# clear 16 random bits
		unknowns = list(set([random.randint(0, 31) for i in range(16)]))
		unknown_mask = functools.reduce(lambda a,b:a|b, [(0x80000000 >> x) for x in unknowns])
		cleared_int = data_int & (~unknown_mask)

		# can we recover the original data?
		recovered = solve_hqx(struct.pack('>I', cleared_int), unknowns, csum_orig)
		(recovered_int,) = struct.unpack('>I', recovered)
		csum_recovered = crc(recovered_int)
		print('crc_b(0x%X) = %s' % (recovered_int, bitstr_int(csum_recovered,16)))
		assert csum_orig == csum_recovered

	crc = crc_hqx_bytes
	for i in range(10000):
		# generate random input, calculate its crc
		alphabet = b'abcdefghijklmnopqrstuvwxyz'
		data = bytes([random.choice(alphabet) for x in range(random.randint(1,50))])
		csum_orig = crc(data)
		print('crc_a(%s) = %s' % (data, bitstr_int(csum_orig,16)))

		# clear 16 random bits
		unknowns = [random.randint(0, 8*len(data)-1) for i in range(16)]
		cleared = list(data)
		for position in unknowns:
			bit = 1<<(7-position%8)
			cleared[position//8] &= ~bit		
		cleared = bytes(cleared)

		# can we recover the original data?
		recovered = solve_hqx(cleared, unknowns, csum_orig)
		csum_recovered = crc(recovered)
		print('crc_b(%s) = %s' % (recovered, bitstr_int(csum_recovered,16)))
		assert csum_orig == csum_recovered

	print('PASS')
