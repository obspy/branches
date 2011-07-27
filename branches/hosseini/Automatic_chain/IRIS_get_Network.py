"""
Returns the available IRIS stations at the IRIS-DMC for all requested events
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
			    #minlat = 20, maxlat = 50, minlon = -124, maxlon = -70, output='xml')
			R = Result.splitlines()
			Stas.append(R)
			#import ipdb; ipdb.set_trace()
			
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
		Station_file1 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHE', 'w')
		pickle.dump(Sta_BHE[i], Station_file1)
		Station_file1.close()
		
		Station_file2 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHN', 'w')
		pickle.dump(Sta_BHN[i], Station_file2)
		Station_file2.close()
		
		Station_file3 = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'All_IRIS_Stations_BHZ', 'w')
		pickle.dump(Sta_BHZ[i], Station_file3)
		Station_file3.close()
		
	t_iris_2 = datetime.now()
	t_iris = t_iris_2 - t_iris_1
	
	print "--------------------"
	print 'IRIS-Time: (Availability)'
	print t_iris	
		
	return Sta_BHE, Sta_BHN, Sta_BHZ, t



# ------------------------Target Dics---------------------------------	
#from lxml import objectify, etree
'''
			Result = client_iris.availability(input['net'], input['sta'], input['loc'], input['cha'], \
				t[i]-10, t[i]+10, lat=input['lat_cba'], lon=input['lon_cba'], minradius=input['mr_cba'], \
				maxradius=input['Mr_cba'], minlat=input['mlat_rbb'], maxlat=input['Mlat_rbb'], \
				minlon=input['mlon_rbb'], maxlon=input['Mlon_rbb'], output='xml')
			    #minlat = 20, maxlat = 50, minlon = -124, maxlon = -70, output='xml')
			
			xml_doc = etree.fromstring(Result)
			xml_doc_string = etree.tostring(xml_doc)
			num_station = xml_doc_string.count('/Station')
	
	
			j=0
			
			for k in range(0, num_station):
				#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
				#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
				Sta_net_code = xml_doc.xpath('/StaMessage/Station')[k].get('net_code')
				Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[k].get('sta_code')
				Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[k].text
				Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[k].text
				Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[i].text
				Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[k].get('loc_code')
				Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[k].get('chan_code')
				#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
				#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
				#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
				#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
				#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
				#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
				#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
				#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
				dic[i][str(k)] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code,\
					'Network': Sta_net_code, 'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
					'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
			#import ipdb; ipdb.set_trace()
	
	
	
	#CHECK!
	#for the first Event!!!
	#len_req_iris_BH = len(dic)
	
	#CHECK!
	#print 'length of required IRIS channels:'
	#print len_req_iris_BH
	
	for i in range(0, len_events):
		#import os
		#folder = os.path.join(Address, 'Data', Period, events[i]['event_id'])
		os.makedirs(Address_events + '/' + events[i]['event_id'])
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS')
	
	
	dic = {}
	dic_target = {}

	j=0
	
	for i in range(0, num_station):
		#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
		#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
		Sta_net_code = xml_doc.xpath('/StaMessage/Station')[i].get('net_code')
		Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[i].get('sta_code')
		Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[i].text
		Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[i].text
		#Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[i].text
		Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[i].get('loc_code')
		Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[i].get('chan_code')
		#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
		#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
		#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + Sta_chan_code \
			+ '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + Sta_End_time, \
			'Network': Sta_net_code, 'Station': Sta_sta_code, 'Start_time': Sta_Start_time, \
			'End_time': Sta_End_time, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
			'Elevation': Sta_Elevation, 'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
		dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code, 'Network': Sta_net_code, \
			'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
			'Location': Sta_loc_code, 'Channel': Sta_chan_code}
	
		#if float(dic[i]['Latitude']) <= 40 and float(dic[i]['Longitude']) <= -110:
			#dic_target[j] ={'Info': Sta_net_code + '--' + Sta_sta_code, \
			'Network': Sta_net_code, 'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon}
		#j += 1
	
	for i in range(0, num_station):
		print dic[i]['Latitude']
	
	print '--------------------------------------------'
	print j
	for k in range(0, j):
		print dic_target[k]
'''
