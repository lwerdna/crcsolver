#!/usr/bin/env python3

# solve the 64-bit CRC given here:
# https://yurichev.com/news/20200416_CRC64/

import random
from crcsolver import solve

def CRC64(data):
	crc = 0xFFFFFFFFFFFFFFFF
	for b in data:
		crc = crc ^ b
		for k in range(8):
			if crc & 1:
				crc = (crc >> 1) ^ 0x42f0e1eba9ea3693
			else:
				crc = (crc >> 1)
	return crc

target_crc = 0x791b385d86c37ffc
assert CRC64(b'lorem ipsum ') == target_crc

print(hex(CRC64(b'lorem ipsum ')))

solutions = set()

random.seed()

while 1:
	unknowns = set(range(8*12))
	# msb of each byte is 0 (ascii)
	unknowns = unknowns - set([x*8 for x in range(12)])
	unknowns = unknowns - set([(x*8)+1 for x in range(12)])
	unknowns = list(unknowns)
	random.shuffle(unknowns)
	solution = solve(b'\x40'*12, unknowns, target_crc, CRC64)

	if solution in solutions:
		continue

	assert CRC64(solution) == target_crc
	solutions.add(solution)
	print(solution)

