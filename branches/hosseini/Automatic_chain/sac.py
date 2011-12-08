import commands
import os
import glob

address = '/media/Elements/TEST_SUMATRA_tarje/2009-09-29_2009-10-01_7.4_8.0/20090930_0000037/'

input_file = open(address + 'IRIS/info/iris_BHZ')

inp = input_file.readlines()
for i in range(0, len(inp)):
	inp[i] = inp[i].split(',')

raw_file = []
resp_file = []

for i in range(0, len(inp)):
	if inp[i][2] == '  ':
		inp[i][2] = ''
	raw_file.append(glob.glob(address + 'IRIS/BH_RAW/' + inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3])) 
	resp_file.append(glob.glob(address + 'IRIS/Resp/RESP.' + inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3]))

for i in range(0, len(raw_file)):
	#import ipdb; ipdb.set_trace()
	print str(i) + '/' + str(len(raw_file))
	i1 = raw_file[i][0]
	i2 = resp_file[i][0]
	i4 = inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3]
	commands.getoutput('./sac.sh' + ' ' + i1 + ' ' + i2 + ' ' + address + ' ' + i4)
