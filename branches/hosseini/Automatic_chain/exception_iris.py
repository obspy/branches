


def exception_iris():
	iris = open('/media/KINGSTON/TEST_NODES/TEST2_NODES/Data/2011-01-08_2011-01-10_6.5_6.8/20110109_0000017/IRIS/EXCEP/Exception_file_IRIS', 'r')
	iris_excep = iris.readlines()
	for i in range(0, len(iris_excep)):
		iris_excep[i] = iris_excep[i].split('---')
	
	for i in range(0, len(iris_excep)):
		if iris_excep[0][3] == 'No waveform data available (HTTPError: )\n':
			print 'OK'
		else:
			print iris_excep[i][0] + '---' + iris_excep[i][1] + '---' + iris_excep[i][2] + '---' + iris_excep[i][3]
			
			


