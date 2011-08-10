"""
Returns available IRIS stations at the IRIS-DMC for all requested events
"""

from obspy.iris import Client as Client_iris
from obspy.core import UTCDateTime
from datetime import datetime
import time
import os
import pickle

client_iris = Client_iris()

def IRIS_get_Network(Address_events, len_events, events, input):
		
	t_iris_1 = datetime.now()
	
	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/RESP/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/EXCEP/')
	
	print "-------------------------------------------------"
	print 'IRIS-Folders are Created!'
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/EXCEP/' + 'Exception_Availability', 'w')
		Report = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Report_station', 'w')
		Exception_file.close()
		Report.close()
	
	t = []
	Stas = []
	
	for i in range(0, len_events):
		
		t.append(UTCDateTime(events[i]['datetime']))
		
		try:		
			
			Result = client_iris.availability(input['net'], input['sta'], input['loc'], input['cha'], \
				t[i]-10, t[i]+10, lat=input['lat_cba'], lon=input['lon_cba'], minradius=input['mr_cba'], \
				maxradius=input['Mr_cba'], minlat=input['mlat_rbb'], maxlat=input['Mlat_rbb'], \
				minlon=input['mlon_rbb'], maxlon=input['Mlon_rbb'], output='bulk')
			    #example:
			    #minlat = 20, maxlat = 50, minlon = -124, maxlon = -70, output='xml')
			
			R = Result.splitlines()
			Stas.append(R)
			
			print 'IRIS-Availability for event: ' + str(i) + '  --->' + 'DONE'

		except Exception, e:
				
			Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/IRIS/EXCEP/' + 'Exception_Availability', 'a')
			ee = 'Event:' + str(i) + '---' + str(e) + '\n'
			
			Exception_file.writelines(ee)
			Exception_file.close()
			print e			

	
	Stas_split = []
	
	for i in range(0, len_events):
		sta = []
		for j in range(0, len(Stas[i])):
			sta.append(Stas[i][j].split(' '))
		Stas_split.append(sta)
	
	
	Sta_BHE = []
	Sta_BHN = []
	Sta_BHZ = []
	
	for i in range(0, len_events):
		sta_BHE = []
		sta_BHN = []
		sta_BHZ = []
		for j in range(0, len(Stas_split[i])):
			if Stas_split[i][j][3] == 'BHE':
				sta_BHE.append(Stas_split[i][j])
			if Stas_split[i][j][3] == 'BHN':
				sta_BHN.append(Stas_split[i][j])
			if Stas_split[i][j][3] == 'BHZ':
				sta_BHZ.append(Stas_split[i][j])
		Sta_BHE.append(sta_BHE)
		Sta_BHN.append(sta_BHN)
		Sta_BHZ.append(sta_BHZ)
		
	
	for i in range(0, len_events):
		print "--------------------"
		print 'IRIS-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len(Sta_BHE[i]))
		print 'IRIS-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len(Sta_BHN[i]))
		print 'IRIS-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len(Sta_BHZ[i]))
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
		eventsID = events[i]['event_id']
		Report.writelines(eventsID + '\n')
		Report.writelines('---------------IRIS---------------' + '\n')
		rep1 = 'IRIS-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len(Sta_BHE[i])) + '\n'
		rep2 = 'IRIS-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len(Sta_BHN[i])) + '\n'
		rep3 = 'IRIS-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len(Sta_BHZ[i])) + '\n'
		Report.writelines(rep1)
		Report.writelines(rep2)
		Report.writelines(rep3)
		Report.writelines('----------------------------------' + '\n')
		Report.close()
		
	
	for i in range(0, len_events):
		Sta_BHE_target = Sta_BHE[i]
		Sta_BHN_target = Sta_BHN[i]
		Sta_BHZ_target = Sta_BHZ[i]
				
		Station_file1 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHE', 'w')
		pickle.dump(Sta_BHE_target, Station_file1)
		Station_file1.close()
		
		Station_file2 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHN', 'w')
		pickle.dump(Sta_BHN_target, Station_file2)
		Station_file2.close()
		
		Station_file3 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHZ', 'w')
		pickle.dump(Sta_BHZ_target, Station_file3)
		Station_file3.close()
	
	t_iris_2 = datetime.now()
	t_iris = t_iris_2 - t_iris_1
	
	print "--------------------"
	print 'IRIS-Time: (Availability)'
	print t_iris	
		
	return Sta_BHE, Sta_BHN, Sta_BHZ, t
