#!/usr/bin/env python3

import sys
import random

class BitMatrix():
	def __init__(self, nrows, ncols):
		self.nrows = nrows
		self.ncols = ncols
		self.rows = [0] * nrows

	def set_identity(self):
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

	def invert(self):
		inv = BitMatrix(self.nrows, self.ncols)
		inv.set_identity()

		rows = list(self.rows)

		for cur in range(self.nrows):
			mask = 1<<(self.ncols-1-cur)

			# find first row with target bit set
			for i in range(cur, self.nrows):
				if rows[i] & mask:
					break
			if i >= self.nrows:
				raise Exception('can\'t invert')

			# if it's not the current row, swap it to current
			if i != cur:
				tmp = rows[cur]
				rows[cur] = rows[i]
				rows[i] = tmp

				tmp = inv.rows[cur]
				inv.rows[cur] = inv.rows[i]
				inv.rows[i] = tmp

			# add to every other row
			for i in range(0, self.nrows):
				if i==cur: continue
				if rows[i] & mask:
					rows[i] ^= rows[cur]
					inv.rows[i] ^= inv.rows[cur]

		# done!
		return inv

	def __mul__(self, rhs):
		if self.ncols != rhs.nrows:
			raise Exception('requested matrices cannot be multiplied')

		new_nrows = self.nrows
		new_ncols = rhs.ncols
		result = BitMatrix(new_ncols, new_nrows)

		for x in range(new_ncols):
			for y in range(new_nrows):
				tmp = self.rows[x] & rhs.get_column(y)
				tmp = sum(map(int, bin(tmp)[2:])) % 2
				if tmp:
					result.rows[y] |= (1<<(new_ncols-1-x))

		return result

	def clone(self):
		tmp = BitMatrix(self.ncols, self.nrows)
		tmp.rows = list(self.rows)
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
	a = BitMatrix(16, 16)

	print('random:')
	a.set_random()
	print(a)

	print('\nidentity:')
	a.set_identity()
	print(a)

	print('\nrandom basis:')
	a.set_random_basis()
	print(a)

	print('\ninverse:')
	b = a.invert()

	print('\ncol[0]:', bin(b.get_column(0)))
	print('col[1]:', bin(b.get_column(1)))
	#print('col[7]:', bin(b.get_column(7)))
	#print('col[8]:', bin(b.get_column(8)))

	#b = BitMatrix(2,2)
	#b.rows = [3,1]

	print('\na:')
	print(a)

	print('\nb:')
	print(b)

	prod = a * b
	print('\nprod:')
	print(prod)

