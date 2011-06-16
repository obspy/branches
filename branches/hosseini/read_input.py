'''
Read inputs from INPUT file
'''

import os

def read_input():
	add = os.getcwd()
	add += '/INPUT'
	f = open(add)
	S = f.readlines()
	Address = S[0].split()[2]
	mind = S[1].split()[2]
	maxd = S[2].split()[2]
	minm = float(S[3].split()[2])
	maxr = int(S[4].split()[2])
	pe = S[6].split()[2]
	
	return Address, mind, maxd, minm, maxr, pe
