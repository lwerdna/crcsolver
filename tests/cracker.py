#!/usr/bin/env python3

import struct
import random
import binascii
import functools

from crccracker import solve

def bitstr_int(val, width):
	return bin(val)[2:].rjust(width, '0')

def bitstr(data):
	return ''.join([bitstr_int(val,8) for val in data])

if __name__ == '__main__':
	def crc_hqx_uint32(x):
		return binascii.crc_hqx(struct.pack('>I', x), 0)
	def crc_hqx_bytes(x):
		return binascii.crc_hqx(x, 0)
	def crc32_uint32(x):
		return binascii.crc32(struct.pack('>I', x), 0)
	def crc32_bytes(x):
		return binascii.crc32(x, 0)
	def findnulls(x):
		lol = [list(range(8*i,8*i+8)) for (i,byte) in enumerate(x) if byte==0]
		return functools.reduce(lambda a,b:a+b, lol, [])

	crc = crc32_uint32
	csum_00 = crc(0x00)
	csum_AA = crc(0xAA)
	print('crc(AA)=%s' % bitstr_int(csum_AA,32))
	csum_01 = crc(0x01) ^ csum_00
	print('crc(01)=%s' % bitstr_int(csum_01,32))
	csum_AB = crc(0xAB)
	print('crc(AB)=%s' % bitstr_int(csum_AB,32))
	assert csum_AB == csum_AA ^ csum_01

	assert solve(b'testes1\x00', range(56,64), 0x2E5A, crc_hqx_bytes) == b'testes12'
	assert solve(b'testes\x002', range(48,56), 0x2E5A, crc_hqx_bytes) == b'testes12'

	assert solve(b'testes1\x00', range(56,64), 0x41979d2b, crc32_bytes) == b'testes12'
	assert solve(b'testes\x002', range(48,56), 0x41979d2b, crc32_bytes) == b'testes12'

	input = b'bl\x00z\x00a\x00d'
	recovered = solve(input, findnulls(input), 0x6B21, crc_hqx_bytes)
	assert crc_hqx_bytes(recovered) == 0x6B21

	input = b'\x14\x56\xB0\x77' # 0xBCAA07F1
	recovered = solve(input, [0,1,2,3], 0xBCAA07F1, crc32_bytes)
	assert crc32_bytes(input) == 0xBCAA07F1

	# integer inputs to crc_hqx()
	for crc in [crc_hqx_bytes, crc32_bytes]:
		for i in range(1000):
			# generate random 32-bit input, calculate its crc
			data = struct.pack('>I', random.getrandbits(32))
			csum_orig = crc(data)
			print('crc_a(%s) = %s' % (data, bitstr_int(csum_orig,32)))

			# clear 16 random bits
			unknowns = list(set([random.randint(0, 31) for i in range(16)]))
			unknown_mask = functools.reduce(lambda a,b:a|b, [(0x80000000 >> x) for x in unknowns])

			cleared = struct.pack('>I', struct.unpack('>I', data)[0] & (~unknown_mask))

			# can we recover the original data?
			recovered = solve(cleared, unknowns, csum_orig, crc)
			csum_recovered = crc(recovered)
			print('crc_b(%s) = %s' % (recovered, bitstr_int(csum_recovered,32)))
			assert csum_orig == csum_recovered

	# string inputs to crc_hqx()
	crc = crc_hqx_bytes
	for i in range(1000):
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
		recovered = solve(cleared, unknowns, csum_orig, crc_hqx_bytes)
		csum_recovered = crc(recovered)
		print('crc_b(%s) = %s' % (recovered, bitstr_int(csum_recovered,16)))
		assert csum_orig == csum_recovered

	print('PASS')
