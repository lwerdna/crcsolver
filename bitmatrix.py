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

	def set_identity(self, relaxed=False):
		if not relaxed and self.nrows != self.ncols:
			raise Exception('cannot compute identity of non-square matrix')

		for i in range(self.nrows):
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

	def row_echelon(self):
		''' calculate row echelon form while recording a history of operations
			row echelon is identity -> history is inverse '''
		nrows = self.nrows
		echelon = self.clone()
		history = BitMatrix(nrows, self.ncols)
		history.set_identity(relaxed=True)

		# row reduce
		for cur in range(nrows):
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

				tmp = history.rows[cur]
				history.rows[cur] = history.rows[i]
				history.rows[i] = tmp

			# add to every other row
			for i in range(0, nrows):
				if i==cur: continue
				if echelon.rows[i] & mask:
					echelon.rows[i] ^= echelon.rows[cur]
					history.rows[i] ^= history.rows[cur]

		return (echelon, history)

	def rank(self, relaxed=False):
		if relaxed:
			echelon = self.clone()
		else:
			(echelon, history) = self.row_echelon()

		rank = 0
		bitpos = self.ncols-1
		for rowi in range(echelon.nrows):
			# find leftmost set bit
			while bitpos >= 0:
				mask = 1<<bitpos
				if echelon.rows[rowi] & mask: break
				bitpos -= 1

			# print('rows[%d]=%s hit bit %d' % (rowi, bin(echelon.rows[rowi])[2:], bitpos))
			if bitpos < 0: break

			# if following row also has set bit, we're done
			if rowi < echelon.nrows-1:
				if echelon.rows[rowi+1] & mask:
					break

			rank += 1
			bitpos -= 1
			if bitpos < 0: break

		return rank

	def inverse(self):
		(echelon, history) = self.clone().row_echelon()
		rank = echelon.rank(relaxed=True)
		if rank != echelon.nrows:
			raise Exception('inversion impossible, matrix rank %d != nrows %d' % (rank, echelon.nrows))
		return history

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

	bm = BitMatrix(3,4, [0xB, 0xC, 0xF])
	(echelon, history) = bm.row_echelon()
	assert echelon == BitMatrix(3,4, [8, 4, 3])
	assert echelon.rank(relaxed=True) == 3

	bm = BitMatrix(3,4, [0xB, 0xC, 0x7])
	(echelon, history) = bm.row_echelon()
	assert echelon == BitMatrix(3,4, [11, 7, 0])
	assert echelon.rank(relaxed=True) == 2

	for i in range(1000):
		dims = random.randint(1,64)

		identity = BitMatrix(dims, dims)
		identity.set_identity()

		basis = BitMatrix(dims, dims)
		basis.set_random_basis()
		print('\nbasis:')
		print(basis)

		inverse = basis.inverse()
		print('\ninverse:')
		print(inverse)

		assert inverse*basis == identity

