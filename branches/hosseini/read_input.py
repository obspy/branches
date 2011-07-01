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
	
	net = S[15].split()[2]
	sta = S[16].split()[2]
	loc = S[17].split()[2]
	cha = S[18].split()[2]
	lat_cba = S[24].split()[2]
	lon_cba = S[25].split()[2]
	mr_cba = S[26].split()[2]
	Mr_cba = S[27].split()[2]
	mlat_rbb = S[28].split()[2]
	Mlat_rbb = S[29].split()[2]
	mlon_rbb = S[30].split()[2]
	Mlon_rbb = S[31].split()[2]
	
	import ipdb; ipdb.set_trace()
	
	return Address, mind, maxd, minm, maxm, minla, maxla, minlo, maxlo, \
		minde, maxde, maxr, pe, net, sta, loc, cha, lat_cba, lon_cba, mr_cba, \
		Mr_cba, mlat_rbb, Mlat_rbb, mlon_rbb, Mlon_rbb
