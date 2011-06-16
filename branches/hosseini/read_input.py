def read_input():
	f = open('/home/kasra/Desktop/INPUT')
	S = f.readlines()
	Add = S[0].split()[2]
	mind = S[1].split()[2]
	maxd = S[2].split()[2]
	minm = float(S[3].split()[2])
	maxr = int(S[4].split()[2])
	pe = S[6].split()[2]
	
	return Add, mind, maxd, minm, maxr, pe
