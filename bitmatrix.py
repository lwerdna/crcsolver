#!/usr/bin/env python3

import sys
import random

class BitMatrix():
	def __init__(self, nrows, ncols, rows=[]):
		self.nrows = nrows
		self.ncols = ncols

		self.rows = [0] * nrows
		for i in range(len(rows)):
			self.rows[i] = rows[i]

		self.check_consistency()

	def check_consistency(self):
		if len(self.rows) > self.nrows:
			raise Exception('%d rows specified, but %d rows found' % (self.nrows, len(self.rows)))

		for row in self.rows:
			if len(bin(row)[2:]) > self.ncols:
				raise Exception('%d columns specified, but 0x%X is wider' % (self.ncols, len(bin(row)[2:])))

	def set_identity(self, relaxed=False):
		if not relaxed and self.nrows != self.ncols:
			raise Exception('cannot compute identity of non-square matrix')

		for i in range(min(self.nrows, self.ncols)):
			self.rows[i] = 1<<(self.ncols-1-i)

	def set_random(self):
		self.rows = [random.getrandbits(self.ncols) for x in range(self.nrows)]

	def set_random_basis(self):
		self.set_identity()
		for i in range(4*self.nrows):
			a = random.randint(0, self.nrows-1)
			b = random.randint(0, self.nrows-1)
			if a != b:
				self.rows[a] ^= self.rows[b]

	def get_column(self, col):
		''' 0-indexed: 0 is leftmost column, self.ncols-1 is rightmost column '''
		if col >= self.ncols:
			raise Exception('requested column %d is out of range' % col)
		mask = 1<<(self.ncols-1-col)
		result = 0
		for row in self.rows:
			result = result << 1
			if row & mask:
				result |= 1
		return result

	def set_column(self, col, value):
		if col >= self.ncols:
			raise Exception('requested column %d is out of range' % col)

		probe = 1<<(self.ncols-1-col)
		for i in range(self.nrows):
			# assume it's a set
			self.rows[i] |= probe
			# if wrong, clear it
			if not (value & (1<<(self.nrows-1-i))):
				self.rows[i] ^= probe

	def row_echelon(self, record=None):
		''' calculate row echelon form
			row echelon is identity -> record is inverse '''

		self.check_consistency()

		(nrows, ncols) = (self.nrows, self.ncols)
		echelon = self.clone()

		# row reduce
		for cur in range(min(nrows, ncols)):
			mask = 1<<(self.ncols-1-cur)

			# find first row with target bit set
			for i in range(cur, nrows):
				if echelon.rows[i] & mask:
					break
			if i >= nrows:
				continue

			# if it's not the current row, swap it to current
			if i != cur:
				tmp = echelon.rows[cur]
				echelon.rows[cur] = echelon.rows[i]
				echelon.rows[i] = tmp

				if record:
					tmp = record.rows[cur]
					record.rows[cur] = record.rows[i]
					record.rows[i] = tmp

			# add to every other row
			for i in range(0, nrows):
				if i==cur: continue
				if echelon.rows[i] & mask:
					echelon.rows[i] ^= echelon.rows[cur]
					if record:
						record.rows[i] ^= record.rows[cur]

		return echelon

	def rank(self):
		''' dimension of the vector space spanned by rows
			assumes row echelon form '''
		return len([x for x in self.rows if x]) # quantity of nonzero rows

	def inverse(self):
		self.check_consistency()

		if self.nrows != self.ncols:
			raise Exception('inversion impossible since rows != columns, %d != %d' % (self.nrows, self.ncols))

		record = BitMatrix(self.nrows, self.ncols)
		record.set_identity()

		echelon = self.row_echelon(record)
		rank = echelon.rank()
		if rank != echelon.nrows:
			raise Exception('inversion impossible, matrix rank %d != nrows %d' % (rank, echelon.nrows))

		return record

	def transpose(self):
		tra = BitMatrix(self.ncols, self.nrows)
		for i in range(self.nrows):
			tra.set_column(i, self.rows[i])
		return tra

	def __mul__(self, rhs):
		if self.ncols != rhs.nrows:
			raise Exception('requested matrices cannot be multiplied')

		new_nrows = self.nrows
		new_ncols = rhs.ncols
		result = BitMatrix(new_nrows, new_ncols)

		for x in range(new_ncols):
			for y in range(new_nrows):
				tmp = self.rows[y] & rhs.get_column(x)
				tmp = sum(map(int, bin(tmp)[2:])) % 2
				if tmp:
					result.rows[y] |= (1<<(new_ncols-1-x))

		return result

	def clone(self):
		tmp = BitMatrix(self.nrows, self.ncols, list(self.rows))
		return tmp

	def __eq__(self, rhs):
		return self.nrows==rhs.nrows and self.ncols==rhs.ncols and self.rows==rhs.rows

	def __neq__(self, rhs):
		return not (self == rhs)

	def __str__(self):
		tmp = [bin(x)[2:] for x in self.rows]
		tmp = ['0'*(self.ncols-len(x))+x for x in tmp]
		return '\n'.join(tmp)

if __name__ == '__main__':
	# test inverse
	# 1000
	# 0100
	# 0010
	# 0001
	bm = BitMatrix(4, 4)
	bm.set_identity()
	assert bm.rows == [8, 4, 2, 1]

	# test inverse, relaxed
	# 10000000
	# 01000000
	# 00100000
	bm = BitMatrix(3, 8) # 1st try
	try:
		bm.set_identity(relaxed=True)
		assert False
	except Exception:
		pass
	bm.set_identity(relaxed=True) # 2nd try
	assert bm.rows == [128, 64, 32]

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

	# test row echelon
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
		A.set_random_basis()
		assert A.inverse() * A == identity

	# solve Ax = B by x = A^-1 * B
#	for i in range(100):
#		dims = random.randint(1,64)
#
#		A = BitMatrix(dims, dims)
#		A.set_random_basis()
#
#		B = BitMatrix(dims, 1)
#		B.set_random()
#
#		inverse = basis.inverse()
#		print('\ninverse:')
#		print(inverse)
#
#		assert inverse*basis == identity
	print('PASS')
