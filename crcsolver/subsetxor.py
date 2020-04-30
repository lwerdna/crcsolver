#!/usr/bin/env python3

import sys
import random
from itertools import compress
from functools import reduce

from .bitmatrix import BitMatrix

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

	record = BitMatrix(len(chosen), len(chosen))
	record.set_identity(relaxed=True)
	echelon = BitMatrix(len(chosen), width, chosen).row_echelon(record)

	# row2mask, eg:
	# [0]: 0x8000 "use row 0 to toggle bit 15"
	# [1]: 0x4000 "use row 1 to toggle bit 14"
	# [2]: 0x0010 "use row 2 to toggle bit 4"
	row2mask = [1<<(echelon.rows[x].bit_length()-1) for x in range(echelon.rank())]

	rows_used_bitfield = 0
	for (row, mask) in enumerate(row2mask):
		if target & mask:
			rows_used_bitfield ^= record.rows[row]

	# selector, eg:
	# [0,1,0,1]
	#  | | | +- chosen[3] used
	#  | | +--- chosen[2] NOT used
	#  | +----- chosen[1] used
	#  +------- chosen[0] NOT used
	selector = [int(x) for x in bitstr(rows_used_bitfield, record.nrows)]
	if target != reduce(lambda a,b:a^b, compress(chosen, selector), 0):
		return []

	# convert selector over chosen to selector over original inputs
	tmp = [0]*len(inputs)
	for (i, s) in enumerate(selector):
		if not s: continue
		tmp[chosen_idxs[i]] = 1
	selector = tmp
	assert target == reduce(lambda a,b:a^b, compress(inputs, selector), 0)

	# done
	return selector

