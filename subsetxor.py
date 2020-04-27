#!/usr/bin/env python3

import sys
import random
from bitmatrix import BitMatrix

from itertools import compress
from functools import reduce

def bitstr(val, width):
	return bin(val)[2:].rjust(width, '0')

def independent_subset(inputs):
	''' given a list of integers, return a list of those that are linearly independent '''

	width = max(x.bit_length() for x in inputs)
	basis = BitMatrix(0, width)

	result = []
	for inp in inputs:
		ranka = basis.rank()
		basis.row_append(inp)
		basis = basis.row_echelon()
		rankb = basis.rank()

		if rankb > ranka:
			result.append(1)
		else:
			result.append(0)
			basis.row_pop()

		# at most n independent vectors of width n
		if basis.nrows >= width:
			result = result + [0]*(len(inputs)-len(result))
			break

	return result

def solve(inputs, target):
	width = max([x.bit_length() for x in inputs])
	if target.bit_length() > width:
		return []

	selector = independent_subset(inputs)
	chosen = list(compress(inputs, selector))
	chosen_idxs = [x for x in range(len(selector)) if selector[x]]

	A = BitMatrix(len(chosen), width, chosen)
	record = BitMatrix(len(chosen), len(chosen))
	record.set_identity(relaxed=True)

	echelon = A.row_echelon(record)

	# calculate row2mask, eg:
	# [0]: 0x8000 "use row 0 to toggle bit 15"
	# [1]: 0x4000 "use row 1 to toggle bit 14"
	# [2]: 0x0010 "use row 2 to toggle bit 4"
	row2mask = [1<<(echelon.rows[x].bit_length()-1) for x in range(echelon.rank())]

	rows_used_bitfield = 0
	for (row, mask) in enumerate(row2mask):
		if target & mask:
			rows_used_bitfield ^= record.rows[row]

	# 0101
	# |||+- row 0 used
	# ||+-- row 1 NOT used
	# |+--- row 2 used
	# +---- row 3 NOT used
	tmp = bitstr(rows_used_bitfield, record.nrows)
	#print('rows_used_bitfield:', tmp)
	selector = [int(x) for x in tmp]

	# [0,1,0,1]
	#print('selector: ', selector)
	# |||+- row 0 used
	# ||+-- row 1 NOT used
	# |+--- row 2 used
	# +---- row 3 NOT used

	# this selector is for the chosen, map these back to the inputs
	tmp = [0]*len(inputs)
	for (i, s) in enumerate(selector):
		if not s: continue
		tmp[chosen_idxs[i]] = 1
	selector = tmp

	# set result to [] if no solution
	if target != reduce(lambda a,b:a^b, compress(inputs, selector), 0):
		return []

	return selector

if __name__ == '__main__':
	# independent subset, they're all independent
	inputs = [0xB, 0xC, 0xF]
	assert independent_subset(inputs) == [1,1,1]

	# independent subset, they're one dependent
	inputs = [0xB, 0xC, 0x7]
	assert independent_subset(inputs) == [1,1,0]

	# independent subset, two dependent, including a zero
	inputs = [9, 11, 0, 2]
	assert independent_subset(inputs) == [1,1,0,0]

	# independent subset, two dependent, including a zero
	inputs = [4, 5, 0, 1]
	assert independent_subset(inputs) == [1,1,0,0]

	# independent subset, many zeros
	inputs = [0,0,0,0,1,0,1,0]
	assert independent_subset(inputs) == [0,0,0,0,1,0,0,0]

	# independent subset
	for testi in range(50):
		# get 8 random 32-bit independent rows
		tmp = BitMatrix(8, 32)
		tmp.set_random_independent_rows()
		inputs = tmp.rows[0:8]
		a = set(inputs)

		# generate 100 DEPENDENT rows
		for k in range(100):
			inputs.append(random.choice(inputs) ^ random.choice(inputs))

		selector = independent_subset(inputs)
		b = set(compress(inputs, selector))

		assert a == b

	# solve a system
	inputs = []
	inputs.append(0b1010)
	inputs.append(0b0011)
	inputs.append(0b1101)
	target = 0b1110
	assert solve(inputs, target) == [0,1,1]

	# solve same system with unnecessary input
	inputs = []
	inputs.append(0b1010)
	inputs.append(0b0011)
	inputs.append(0b1101)
	inputs.append(0b0111)
	target = 0b1110
	assert solve(inputs, target) == [0,1,1,0]

	# solve an 11-bit known system
	inputs = []
	inputs.append(0b11100111011)
	inputs.append(0b01010000110)
	inputs.append(0b11001011100)
	inputs.append(0b01111101011)
	inputs.append(0b01010110011)
	inputs.append(0b01000101000)
	inputs.append(0b10001001011)
	inputs.append(0b00011001010)
	inputs.append(0b11000100111)
	inputs.append(0b11000100001)
	inputs.append(0b10011010011)
	inputs.append(0b11010111010)
	inputs.append(0b10111000101)
	target =      0b10011011010
	assert solve(inputs, target) == [0,1,1,0,0,0,0,0,0,0,0,0,0]

	# solve a 4-bit known system (worked on paper)
	inputs = [0xA, 0x3, 0xD, 0xF]
	assert solve(inputs, 0xA) == [1,0,0,0]
	assert solve(inputs, 0x3) == [0,1,0,0]
	assert solve(inputs, 0xD) == [0,0,1,0]
	assert solve(inputs, 0xF) == [0,0,0,1]

	# solve stupid cases
	inputs = [1,0,1,0]
	assert solve(inputs, 1) == [1,0,0,0]

	# more zeros
	inputs = [0,0,0,0,1,0,1,0]
	assert solve(inputs, 1) == [0,0,0,0,1,0,0,0]

	# solve a 4-bit known system (worked on paper)
	inputs = [0xA, 0x3, 0xD, 0xF]
	assert solve(inputs, 0xA) == [1,0,0,0]
	assert solve(inputs, 0x3) == [0,1,0,0]
	assert solve(inputs, 0xD) == [0,0,1,0]
	assert solve(inputs, 0xF) == [0,0,0,1]

	for target in range(16):
		selector = solve(inputs, target)
		check = reduce(lambda a,b:a^b, compress(inputs, selector), 0)
		assert check == target

	# solve a known system (worked on paper)
	inputs = [0x18, 0xA, 0x1F, 0x17]
	assert solve(inputs, 0) == [0,0,0,0]
	assert solve(inputs, 5) == [1,1,0,1]

	# solve problems with full inverses
	for testi in range(20):
		width = random.randint(1,32)

		# generate inputs known to solve
		tmp = BitMatrix(width,width)
		tmp.set_random_independent_rows()
		inputs = tmp.rows

		for i in range(100):
			target = random.getrandbits(width)
			selector = solve(inputs, target)
			assert target == reduce(lambda a,b:a^b, compress(inputs, selector), 0)

	# solve problems without full inverses
	for testi in range(10000):
		width = random.randint(1,32)
		target = random.getrandbits(width)
		inputs = [target]
		# add the inputs that can produce the target
		for i in range(6):
			plain = inputs.pop()
			key = random.getrandbits(width)
			inputs.append(plain ^ key)
			inputs.append(key)
		# add some random inputs (that may not necessarily help in producing the target)
		for i in range(6):
			inputs.append(random.getrandbits(width))
		# mix it all up
		random.shuffle(inputs)

		selector = solve(inputs, target)
		check = reduce(lambda a,b:a^b, compress(inputs, selector), 0)
		assert target == check

	# TODO: construct and test systems WITHOUT solutions

	print('PASS')
