


def exception_arc():
	arc = open('/media/KINGSTON/TEST_NODES/TEST2_NODES/Data/2011-01-08_2011-01-10_6.5_6.8/20110109_0000017/ARC/EXCEP/Exception_file_ARC', 'r')
	arc_excep = arc.readlines()
	for i in range(0, len(arc_excep)):
		arc_excep[i] = arc_excep[i].split('---')
	
	for i in range(0, len(arc_excep)):
		if arc_excep[0][3] == 'No waveform data available (HTTPError: )\n':
			print 'OK'
		elif arc_excep[0][3] == "(110, 'Connection timed out')\n"
			print arc_excep[i][0] + '---' + arc_excep[i][1] + '---' + arc_excep[i][2] + '---' + arc_excep[i][3]
