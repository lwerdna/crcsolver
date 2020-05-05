#!/usr/bin/env python3

# keygen for http://crackmes.cf/users/andrewl.us/capriccio/

import sys
from struct import unpack

from crcsolver import solve

def crc64(data):
	crc = 0
	for b in data:
		crc = crc ^ b
		for k in range(8):
			if crc & 1:
				crc = (crc >> 1) ^ 0xC96C5795D7870F42
			else:
				crc = (crc >> 1)
	return crc

def gen_key_for_name(name):
	region = list(b'      GF(2^64)[X]/(x^64 + x^62 + x^57 + x^55 + x^54 + x^53 + x^52 + x^47 + x^46 + x^45 + x^40 + x^39 + x^38 + x^37 + x^35 + x^33 + x^32 + x^31 + x^29 + x^27 + x^24 + x^23 + x^22 + x^21 + x^19 + x^17 + x^13 + x^12 + x^10 + x^9 + x^7 + x^4 + x^1 + 1)       \0')
	assert len(region) == 256

	# spread the name over the region
	for i in range(len(name)):
		region[i<<4] = ord(name[i])

	# where serial is positioned
	oserial = len(name)*4
	unknowns = list(range(8*oserial, 8*(oserial+8)))
	assert len(unknowns) == 64

	target_crc = 0x6963636972706163 # "capricci"
	solution = solve(bytes(region), unknowns, target_crc, crc64)
	return unpack('<Q', solution[oserial:oserial+8])[0]

if __name__ == '__main__':
	assert gen_key_for_name('aardvark') == 0x1D82940F23811121
	assert gen_key_for_name('abcdef') == 0xA906EDBA84A6D5AE
	assert gen_key_for_name('papanyquiL') == 0x2EB59FC14E5374C4
	assert gen_key_for_name('Vallani') == 0x67E851E7178F8419 
	assert gen_key_for_name('andrewl') == 0x879FD586E7E403A2
	print('PASS!')

	if sys.argv[1:]:
		name = sys.argv[1]
		serial = gen_key_for_name(name)
		print('-------------------------')
		print('   user: %s' % name)
		print(' serial: %X' % serial)
		print('-------------------------')
