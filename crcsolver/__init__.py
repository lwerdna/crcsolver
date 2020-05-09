name = "crcsolver"

from . import main

def solve(data, unknowns, desired, crc_func):
	return main.solve(data, unknowns, desired, crc_func)

def compute(data, crc_name):
	return main.compute(data, crc_name)
