#!/usr/bin/env python3

import sys
import random
from bitmatrix import BitMatrix

from itertools import compress
from functools import reduce

def solve(width, inputs, target):
	# 11000
	# 01010
	# 11111
	# 10111
	A = BitMatrix(len(inputs), width)
	for i in range(len(inputs)):
		A.rows[i] = inputs[i]

	#
	(echelon, history) = A.row_echelon()

	#
	bit2row = {}
	for bit in range(width-1,-1,-1):
		# which rows have this bit set?
		matches = list(filter(lambda i: echelon.rows[i] & (1<<bit), range(len(echelon.rows))))
		if len(matches) == 0: continue
		if len(matches) > 2: break # NOT a pivot if multiple rows have this bit!
		bit2row[bit] = matches[0]
		if len(bit2row) >= len(echelon.rows): break

	rowflags = 0
	for (bit,row) in bit2row.items():
		if target & (1<<bit):
			rowflags ^= history.rows[row]

	print('rowflags:', bin(rowflags)[2:])
	tmp = bin(rowflags)[2:]
	tmp = '0'*(width-len(tmp))+tmp
	selector = [int(x) for x in tmp]

	# set result to [] if no solution
	if target != reduce(lambda a,b:a^b, compress(inputs, selector), 0):
		return []

	selector = selector[0:len(inputs)]
	print('returning:', selector)
	return selector

if __name__ == '__main__':
	# solve stupid cases
	inputs = [1,0,1,0]
	assert solve(1, inputs, 1) == [1,0]
	sys.exit(-1)

	# solve a 4-bit known system (worked on paper)
	inputs = [0xA, 0x3, 0xD, 0xF]
	assert solve(4, inputs, 0xA) == [1,0,0,0]
	assert solve(4, inputs, 0x3) == [0,1,0,0]
	assert solve(4, inputs, 0xD) == [0,0,1,0]
	assert solve(4, inputs, 0xF) == [0,0,0,1]

	for target in range(16):
		selector = solve(4, inputs, target)
		check = reduce(lambda a,b:a^b, compress(inputs, selector), 0)
		assert check == target

	# solve a known system (worked on paper)
	inputs = [0x18, 0xA, 0x1F, 0x17]
	assert solve(5, inputs, 0) == [0,0,0,0]
	assert solve(5, inputs, 5) == [1,1,0,1]

	# solve problems with full inverses
	for testi in range(20):
		width = random.randint(1,20)

		# generate inputs known to solve
		tmp = BitMatrix(width,width)
		tmp.set_random_basis()
		inputs = tmp.rows

		for i in range(100):
			target = random.getrandbits(width)
			selector = solve(width, inputs, target)
			assert target == reduce(lambda a,b:a^b, compress(inputs, selector), 0)

	for testi in range(20):
		width = random.randint(1,2)

		# solve problems with partial inverses
		target = random.getrandbits(width)
		inputs = [target]
		# add the inputs that can produce the target
		for i in range(6):
			key = random.getrandbits(width)
			inputs.append(inputs.pop() ^ key)
			inputs.append(key)
		# add some random inputs
		for i in range(6):
			inputs.append(random.getrandbits(width))
		# shuffle the inputs
		random.shuffle(inputs)

		print('inputs:')
		print(BitMatrix(len(inputs), width, inputs))
		print('target:\n', bin(target)[2:])

		selector = solve(width, inputs, target)
		assert target == reduce(lambda a,b:a^b, compress(inputs, selector), 0)

