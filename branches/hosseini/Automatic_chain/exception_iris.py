


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
			
			

for update:
 - creat a folder that contains all available station FOR UPDATING
 - do the same procedure for getting the waveform and ....
 - remove the folder for updating
	
arc = open('/media/KINGSTON/TEST_NODES/TEST2_NODES/Data/2011-01-08_2011-01-10_6.5_6.8/20110109_0000017/ARC/STATION/All_ARC_Stations_BHE', 'r')
a = pickle.load(arc)

for k in range(0, len_events):
		List_IRIS_BHE.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHE'))
		List_IRIS_BHN.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHN'))
		List_IRIS_BHZ.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHZ'))

		List_IRIS_BHE[k] = sorted(List_IRIS_BHE[k])
		List_IRIS_BHN[k] = sorted(List_IRIS_BHN[k])
		List_IRIS_BHZ[k] = sorted(List_IRIS_BHZ[k])



		for i in range(0, len(List_IRIS_BHE[k])):
			st = read(List_IRIS_BHE[k][i])
			sta_BHE = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
			Sta_BHE.append(sta_BHE)

for k in range(0, len_events):
	for i in range(0, len(a)):
		for j in range(0, len(List_IRIS_BHE[k]))
		if a[i][0] == 'WM':
			if a[i][1] == 'MAHO':
				if a[i][2] == '':
					if a[i][3] == 'BHE':
						a.remove(a[i])
