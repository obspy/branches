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
	maxm = float(S[4].split()[2])
	minla = float(S[5].split()[2])
	maxla = float(S[6].split()[2])
	minlo = float(S[7].split()[2])
	maxlo = float(S[8].split()[2])
	minde = float(S[9].split()[2])
	maxde = float(S[10].split()[2])
	maxr = int(S[11].split()[2])
	pe = S[13].split()[2]
	
	return Address, mind, maxd, minm, maxm, minla, maxla, minlo, maxlo, \
		minde, maxde, maxr, pe
	
