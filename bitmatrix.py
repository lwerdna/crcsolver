#!/usr/bin/env python3

import random

class BitMatrix():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.rows = []

	def random(self):
		self.rows = [random.getrandbits(self.width) for x in range(self.height)]

	def identity(self):
		for i in range(self.height):
			self.rows[i] = 1<<(self.width-i-1)

	def random_basis(self):
		self.identity()
		for i in range(4*self.height):
			a = random.randint(0, self.height-1)
			b = random.randint(0, self.height-1)
			if a != b:
				self.rows[a] ^= self.rows[b]

	def __str__(self):
		tmp = [bin(x)[2:] for x in self.rows]
		tmp = ['0'*(self.width-len(x))+x for x in tmp]
		return '\n'.join(tmp)

if __name__ == '__main__':
	bm = BitMatrix(8, 8)

	print('random:')
	bm.random()
	print(bm)

	print('identity:')
	bm.identity()
	print(bm)

	print('random basis:')
	bm.random_basis()
	print(bm)
