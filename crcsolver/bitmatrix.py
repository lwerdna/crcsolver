#!/usr/bin/env python3

import sys
import random

class MatrixException(Exception):
	pass

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
			raise MatrixException('%d rows specified, but %d rows found' % (self.nrows, len(self.rows)))

		for row in self.rows:
			if row.bit_length() > self.ncols:
				raise MatrixException('%d columns specified, but 0x%X is wider' % (self.ncols, row))

	def set_identity(self, relaxed=False):
		if not relaxed and self.nrows != self.ncols:
			raise MatrixException('cannot compute identity of non-square matrix')

		for i in range(min(self.nrows, self.ncols)):
			self.rows[i] = 1<<(self.ncols-1-i)

	def set_random(self):
		self.rows = [random.getrandbits(self.ncols) for x in range(self.nrows)]

	def set_random_independent_rows(self):
		''' this is a basis if nrows==ncols '''
		self.check_consistency()

		if self.nrows > self.ncols:
			raise MatrixException('%d %d-bit rows cannot all be independent' % (self.nrows, self.ncols))

		self.set_identity(relaxed=True)
		for i in range(4*self.nrows):
			a = random.randint(0, self.nrows-1)
			b = random.randint(0, self.nrows-1)
			if a != b:
				self.rows[a] ^= self.rows[b]

	def get_column(self, col):
		''' 0-indexed: 0 is leftmost column, self.ncols-1 is rightmost column '''
		if col >= self.ncols:
			raise MatrixException('requested column %d is out of range' % col)
		mask = 1<<(self.ncols-1-col)
		result = 0
		for row in self.rows:
			result = result << 1
			if row & mask:
				result |= 1
		return result

	def set_column(self, col, value):
		if col >= self.ncols:
			raise MatrixException('requested column %d is out of range' % col)

		probe = 1<<(self.ncols-1-col)
		for i in range(self.nrows):
			# assume it's a set
			self.rows[i] |= probe
			# if wrong, clear it
			if not (value & (1<<(self.nrows-1-i))):
				self.rows[i] ^= probe

	def row_append(self, row):
		self.check_consistency()

		if row >= (1<<self.ncols):
			raise MatrixException('cannot append 0x%X as its width exceeds columns %d' % (row, self.ncols))

		self.nrows += 1
		self.rows.append(row)

	def row_pop(self):
		self.check_consistency()

		if self.nrows <= 0:
			raise MatrixException('attempting to pop a row from empty row matrix')

		self.nrows -= 1
		return self.rows.pop()

	def row_echelon(self, record=None):
		''' calculate row echelon form
			row echelon is identity -> record is inverse '''

		self.check_consistency()
		(nrows, ncols) = (self.nrows, self.ncols)

		# use a dummy record if no reference provided
		if not record:
			record = BitMatrix(nrows, 1)

		record.check_consistency()
		if self.nrows != record.nrows:
			raise MatrixException('record matrix has %d rows, mismatch our %d rows' % (record.nrows, self.nrows))

		pos = 0
		echelon = self.clone()
		for mask in [1<<x for x in range(ncols-1,-1,-1)]:
			# find first index with bit set
			miss = True
			for i in range(pos, nrows):
				if echelon.rows[i] & mask:
					miss = False; break
			if miss: continue

			# swap into position
			if i != pos:
				(echelon.rows[i], echelon.rows[pos]) = (echelon.rows[pos], echelon.rows[i])
				(record.rows[i], record.rows[pos]) = (record.rows[pos], record.rows[i])

			# add it to all applicable rows
			for i in (x for x in range(nrows) if x!=pos):
				if echelon.rows[i] & mask:
					echelon.rows[i] ^= echelon.rows[pos]
					record.rows[i] ^= record.rows[pos]

			pos += 1
			if pos >= nrows:
				break

		return echelon

	def rank(self):
		''' dimension of the vector space spanned by rows
			assumes row echelon form '''
		return len([x for x in self.rows if x]) # quantity of nonzero rows

	def inverse(self):
		self.check_consistency()

		if self.nrows != self.ncols:
			raise MatrixException('inversion impossible since rows != columns, %d != %d' % (self.nrows, self.ncols))

		record = BitMatrix(self.nrows, self.ncols)
		record.set_identity()

		echelon = self.row_echelon(record)
		rank = echelon.rank()
		if rank != echelon.nrows:
			raise MatrixException('inversion impossible, rank %d != nrows %d' % (rank, echelon.nrows))

		return record

	def transpose(self):
		tra = BitMatrix(self.ncols, self.nrows)
		for i in range(self.nrows):
			tra.set_column(i, self.rows[i])
		return tra

	def __mul__(self, rhs):
		if self.ncols != rhs.nrows:
			raise MatrixException('requested factors cannot be multiplied')

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
