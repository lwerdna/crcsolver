#!/usr/bin/env python3

import random

from crcsolver.bitmatrix import BitMatrix, MatrixException

if __name__ == '__main__':
	# test identity
	# 1000
	# 0100
	# 0010
	# 0001
	bm = BitMatrix(4, 4)
	bm.set_identity()
	assert bm.rows == [8, 4, 2, 1]

	# test identity, relaxed
	# 10000000
	# 01000000
	# 00100000
	bm = BitMatrix(3, 8) # 1st try
	try:
		bm.set_identity()
		print('FAIL')
		assert False
	except MatrixException:
		pass
	bm.set_identity(relaxed=True) # 2nd try
	assert bm.rows == [128, 64, 32]

	# test append
	bm = BitMatrix(3, 8, [128,64,32])
	bm.row_append(16)
	bm.row_append(8)
	bm.row_append(4)
	bm.row_append(2)
	bm.row_append(1)
	assert bm.rows == [128, 64, 32, 16, 8, 4, 2, 1]
	bm.row_append(255)
	allowed = True
	try:
		bm.row_append(256)
		print('FAIL')
		assert False
	except MatrixException:
		pass

	# test row echelon
	# 1011    1000
	# 1100 -> 0100
	# 1111    0011
	bm = BitMatrix(3,4, [0xB, 0xC, 0xF])
	echelon = bm.row_echelon()
	assert echelon == BitMatrix(3,4, [8, 4, 3])
	assert echelon.rank() == 3

	# test row echelon, with degenerate row
	# 1011    1000
	# 1100 -> 0100
	# 0111    0000
	bm = BitMatrix(3,4, [0xB, 0xC, 0x7])
	echelon = bm.row_echelon()
	assert echelon == BitMatrix(3,4, [11, 7, 0])
	assert echelon.rank() == 2

	# test row echelon, with degenerate zero row
	# 1001    1001
	# 1011 -> 0010
	# 0000    0000
	# 0010    0000
	bm = BitMatrix(4,4, [9,11,0,2])
	echelon = bm.row_echelon()
	assert echelon == BitMatrix(4,4, [9,2,0,0])
	assert echelon.rank() == 2

	# test TALL row echelon
	# 1      1
	# 0   -> 0
	# 1      0
	# ...    ...
	bm = BitMatrix(1000,1)
	bm.set_random()
	echelon = bm.row_echelon()
	assert echelon == BitMatrix(1000,1, [1]+999*[0])
	assert echelon.rank() == 1

	# test A^-1 * A = 1
	for i in range(100):
		dims = random.randint(1,64)

		identity = BitMatrix(dims, dims)
		identity.set_identity()

		A = BitMatrix(dims, dims)
		A.set_random_independent_rows()
		assert A.inverse() * A == identity

	# solve Ax = B by x = A^-1 * B
#	for i in range(100):
#		dims = random.randint(1,64)
#
#		A = BitMatrix(dims, dims)
#		A.set_random_independent_rows()
#
#		B = BitMatrix(dims, 1)
#		B.set_random()
#
#		inverse = A.inverse()
#		#print('\ninverse:')
#		#print(inverse)
#
#		assert inverse*A == identity

	print('PASS')
