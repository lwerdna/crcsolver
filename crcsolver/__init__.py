name = "crcsolver"

from . import main

def solve(data, unknowns, desired, crcfunc):
	return main.solve(data, unknowns, desired, crcfunc)
