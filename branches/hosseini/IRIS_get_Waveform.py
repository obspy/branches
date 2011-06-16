'''
Getting Waveform from IRIS web-service based on the desired events...
'''

from datetime import datetime
import time
import pickle
from obspy.iris import Client as Client_iris

client_iris = Client_iris()

def IRIS_get_Waveform(Address, Period, len_events, events, Networks_iris, t):
	
	for i in range(0, len_events):
		Exception_file = open(Address + '/Data/' + Period + '/' + \
			events[i]['event_id'] + '/IRIS/' + 'Exception_file_IRIS', 'w')
		Exception_file.close()
		
	t_wave_1 = datetime.now()
	
	Len_Lat_Lon = []
	Lat = []
	Lon = []
	name = []

	client_iris = Client_iris()
	
	for i in range(0, len_events):
		
		Lat_temp = []
		Lon_temp = []
		name_temp = []
		len_req_iris_BH = len(Networks_iris[i]) 
		
		
		for j in range(0, len_req_iris_BH):
		#for j in range(0,10):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'IRIS-Event and Station Numbers are:'
			print EC + '-BHE'
			try:
				client_iris = Client_iris()
				
				# BHE
				st = client_iris.getWaveform(Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station'], \
					Networks_iris[i][str(j)]['Location'], 'BHE', t[i]-300, t[i]+4800)
				iris_BH_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + Networks_iris[i][str(j)]['Location'] + \
					'-' + 'BHE', 'a')
				pickle.dump(st, iris_BH_file)
				iris_BH_file.close()
				
			except Exception, e:	
				print Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station']
				
				Exception_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + 'Exception_file_IRIS', 'a')

				ee = str(i) + str(j) + '-' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + \
					Networks_iris[i][str(j)]['Location'] + '-' + 'BHE' + \
					'---' + str(e) + '\n'
				
				Exception_file.writelines(ee)
				print e
		
		for j in range(0, len_req_iris_BH):
		#for j in range(0,10):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'IRIS-Event and Station Numbers are:'
			print EC + '-BHN'
			try:
				client_iris = Client_iris()
				
				# BHN
				st = client_iris.getWaveform(Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station'], \
					Networks_iris[i][str(j)]['Location'], 'BHN', t[i]-300, t[i]+4800)
				iris_BH_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + Networks_iris[i][str(j)]['Location'] + \
					'-' + 'BHN', 'a')
				pickle.dump(st, iris_BH_file)
				iris_BH_file.close()
				
			except Exception, e:	
				print Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station']
				
				Exception_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + 'Exception_file_IRIS', 'a')

				ee = str(i) + str(j) + '-' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + \
					Networks_iris[i][str(j)]['Location'] + '-' + 'BHN' + \
					'---' + str(e) + '\n'
				
				Exception_file.writelines(ee)
				print e
		
		
		#for j in range(0, len_req_iris_BH):
		#for j in range(0, len_req_iris_BH, 35):
		for j in range(0,10):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'IRIS-Event and Station Numbers are:'
			print EC + '-BHZ'
			try:
				client_iris = Client_iris()
				
				# BHZ
				st = client_iris.getWaveform(Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station'], \
					Networks_iris[i][str(j)]['Location'], 'BHZ', t[i]-300, t[i]+4800)
				iris_BH_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + Networks_iris[i][str(j)]['Location'] + \
					'-' + 'BHZ', 'a')
				pickle.dump(st, iris_BH_file)
				#import ipdb; ipdb.set_trace()
				iris_BH_file.close()
				
				Lat_temp.append([i, Networks_iris[i][str(j)]['Latitude']])
				Lon_temp.append([i, Networks_iris[i][str(j)]['Longitude']])
				name_temp.append([i, Networks_iris[i][str(j)]['Network'] + '.' + \
					Networks_iris[i][str(j)]['Station']])
				Lat.append([i, Networks_iris[i][str(j)]['Latitude']])
				Lon.append([i, Networks_iris[i][str(j)]['Longitude']])
				name.append([i, Networks_iris[i][str(j)]['Network'] + '.' +Networks_iris[i][str(j)]['Station']])
				# client_arclink.saveResponse(Address + '/Data/' + Period + \
				#'/' + events[i]['event_id'] + '/Arc_BH/' + 'Resp/' + str(Nets_Arc_req_BHE[i][j][0]) + \
				#'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BH', \
				#Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], Nets_Arc_req_BHE[i][j][2], 'BH*', t[i]-300, t[i]+4800)
               
			except Exception, e:	
				print Networks_iris[i][str(j)]['Network'], Networks_iris[i][str(j)]['Station']
				
				Exception_file = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/IRIS/' + 'Exception_file_IRIS', 'a')

				ee = str(i) + str(j) + '-' + Networks_iris[i][str(j)]['Network'] + \
					'-' + Networks_iris[i][str(j)]['Station'] + '-' + \
					Networks_iris[i][str(j)]['Location'] + '-' + 'BHZ' + \
					'---' + str(e) + '\n'
				
				Exception_file.writelines(ee)
				print e
				
		Len_Lat_Lon.append(len(Lat_temp)) 
	
	return Lat, Lon, name, Len_Lat_Lon
	
	print 'Arclink and BH* is DONE'

	Exception_file1.close()
	Exception_file2.close()
	
	t_wave_2 = datetime.now()
	t_wave = t_wave_2 - t_wave_1
	
	print "Time for getting Waveforms from Arclink:"
	print t_wave
