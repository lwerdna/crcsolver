#!/usr/bin/env python3

import sys
import random
from bitmatrix import BitMatrix

def solve(width, inputs, output):
	# currently support only "square" inputs
	# eg: 32 values, each 32-bits
	assert width == len(inputs)

	# set up Ax = B
	A = BitMatrix(width, width)
	for (i, inp) in enumerate(inputs):
		A.set_column(i, inp)

	B = BitMatrix(width, 1)
	B.set_column(0, output)

	x = A.inverse()*B

	# 0x2A -> [0,0,1,0,1,0,1,0]
	col = x.get_column(0)
	return [int(bool(col & (1<<(width-1-i)))) for i in range(width)]

if __name__ == '__main__':
	inputs = [0xA, 0x3, 0xD, 0xF]
	assert solve(4, inputs, 0xA) == [1,0,0,0]
	assert solve(4, inputs, 0x3) == [0,1,0,0]
	assert solve(4, inputs, 0xD) == [0,0,1,0]
	assert solve(4, inputs, 0xF) == [0,0,0,1]

	for target in range(16):
		answer = solve(4, inputs, target)
		check = 0
		for (idx,flag) in enumerate(answer):
			if flag:
				check ^= inputs[idx]
		assert check == target

	# get random bit size
	for testi in range(100):
		width = random.randint(1,100)

		# generate inputs known to solve
		tmp = BitMatrix(width,width)
		tmp.set_random_basis()
		inputs = tmp.rows

		for targeti in range(100):
			target = random.getrandbits(width)
			print('solving for: 0x%X' % target)
			answer = solve(width, inputs, target)
			check = 0
			for (idx,flag) in enumerate(answer):
				if flag:
					check ^= inputs[idx]
			assert check == target
