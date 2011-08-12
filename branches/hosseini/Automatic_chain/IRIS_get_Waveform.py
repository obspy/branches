"""
Gets Waveforms, Response files and other information from IRIS web-service based on the requested events...
"""

from datetime import datetime
import time
import pickle
from obspy.iris import Client as Client_iris
import os
from lxml import etree


def IRIS_get_Waveform(input, Networks_iris_BHE, \
	Networks_iris_BHN, Networks_iris_BHZ, t):
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/Data/' + Period
	
	Event_file = open(Address_events + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	#if os.path.exists() == True:
		
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/EXCEP/' + 'Exception_file_IRIS', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------IRIS----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Avail_IRIS_Stations_BHE', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Avail_IRIS_Stations_BHN', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Avail_IRIS_Stations_BHZ', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Input_Syn_BHE', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Input_Syn_BHN', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Input_Syn_BHZ', 'w')
		Syn_file.close()
	
	
	
	for i in range(0, len_events):
		
		t_wave_1 = datetime.now()
		
		if input['TEST'] == 'Y':
			len_req_iris_BHE = input['TEST_no']
			len_req_iris_BHN = input['TEST_no']
			len_req_iris_BHZ = input['TEST_no']

		else:	
			len_req_iris_BHE = len(Networks_iris_BHE[i]) 
			len_req_iris_BHN = len(Networks_iris_BHN[i])
			len_req_iris_BHZ = len(Networks_iris_BHZ[i])
		
		dic_BHE = {}		
				
		if input['BHE'] == 'Y':
			
			for j in range(0, len_req_iris_BHE):
			
				print '------------------'
				print 'IRIS-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHE'
				try:
					
					client_iris = Client_iris()
					
					# BHE
					dummy = 'Waveform'
					
					client_iris.saveWaveform(Address_events + '/' + events[i]['event_id'] +\
						'/IRIS/' + Networks_iris_BHE[i][j][0] +	'.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE', Networks_iris_BHE[i][j][0], Networks_iris_BHE[i][j][1], \
						Networks_iris_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Networks_iris_BHE[i][j][0] + '.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"  
					
					dummy = 'Response'
					
					client_iris.saveResponse(Address_events + '/' +	events[i]['event_id'] + \
						'/IRIS/RESP/' + 'RESP' + '.' + Networks_iris_BHE[i][j][0] +	'.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE', Networks_iris_BHE[i][j][0], Networks_iris_BHE[i][j][1], \
						Networks_iris_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Response for: " + Networks_iris_BHE[i][j][0] + '.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
					
					'''
					dummy = 'sacpz'
					
					import ipdb; ipdb.set_trace()
					
					sacpz = client_iris.sacpz(network=Networks_iris_BHE[i][j][0], \
						station=Networks_iris_BHE[i][j][1], location=Networks_iris_BHE[i][j][2], \
						channel="BHE", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'availability'
					
					avail = client_iris.availability(network=Networks_iris_BHE[i][j][0], \
						station=Networks_iris_BHE[i][j][1], location=Networks_iris_BHE[i][j][2], \
						channel="BHE", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'], output = 'xml')
					
					
					xml_doc = etree.fromstring(avail)
							
					#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
					#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
					Sta_net_code = xml_doc.xpath('/StaMessage/Station')[0].get('net_code')
					Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[0].get('sta_code')
					Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[0].text
					Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[0].text
					Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[0].text
					Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('loc_code')
					Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('chan_code')
					#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
					#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
					#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
					#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
					#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
					#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
					#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
					#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
					dic_BHE[j] = {'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/IRIS/STATION/' + 'Input_Syn_BHE', 'a')
					syn = dic_BHE[j]['Network'] + ' , ' + dic_BHE[j]['Station'] + ' , ' + \
						dic_BHE[j]['Location'] + ' , ' + dic_BHE[j]['Channel'] + ' , ' + dic_BHE[j]['Latitude'] + \
						' , ' + dic_BHE[j]['Longitude'] + ' , ' + dic_BHE[j]['Elevation'] + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Networks_iris_BHE[i][j][0] +	'.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Networks_iris_BHE[i][j][0] +	'.' + Networks_iris_BHE[i][j][1] + \
						'.' +Networks_iris_BHE[i][j][2] + '.' + 'BHE'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Networks_iris_BHE[i][j][0] + \
						'.' + Networks_iris_BHE[i][j][1] + '.' + \
						Networks_iris_BHE[i][j][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHE', 'a')
		pickle.dump(dic_BHE, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'IRIS-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(dic_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
			
				
		
		dic_BHN = {}		
				
		if input['BHN'] == 'Y':
			
			for j in range(0, len_req_iris_BHN):
			
				print '------------------'
				print 'IRIS-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHN'
				try:
					
					client_iris = Client_iris()
					
					# BHN
					dummy = 'Waveform'
					
					client_iris.saveWaveform(Address_events + '/' + events[i]['event_id'] +\
						'/IRIS/' + Networks_iris_BHN[i][j][0] +	'.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN', Networks_iris_BHN[i][j][0], Networks_iris_BHN[i][j][1], \
						Networks_iris_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Networks_iris_BHN[i][j][0] + '.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"  
					
					dummy = 'Response'
					
					client_iris.saveResponse(Address_events + '/' +	events[i]['event_id'] + \
						'/IRIS/RESP/' + 'RESP' + '.' + Networks_iris_BHN[i][j][0] +	'.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN', Networks_iris_BHN[i][j][0], Networks_iris_BHN[i][j][1], \
						Networks_iris_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Response for: " + Networks_iris_BHN[i][j][0] + '.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
					
					'''
					dummy = 'sacpz'
					
					import ipdb; ipdb.set_trace()
					
					sacpz = client_iris.sacpz(network=Networks_iris_BHN[i][j][0], \
						station=Networks_iris_BHN[i][j][1], location=Networks_iris_BHN[i][j][2], \
						channel="BHN", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'availability'
					
					avail = client_iris.availability(network=Networks_iris_BHN[i][j][0], \
						station=Networks_iris_BHN[i][j][1], location=Networks_iris_BHN[i][j][2], \
						channel="BHN", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'], output = 'xml')
					
					
					xml_doc = etree.fromstring(avail)
							
					#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
					#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
					Sta_net_code = xml_doc.xpath('/StaMessage/Station')[0].get('net_code')
					Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[0].get('sta_code')
					Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[0].text
					Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[0].text
					Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[0].text
					Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('loc_code')
					Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('chan_code')
					#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
					#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
					#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
					#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
					#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
					#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
					#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
					#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
					dic_BHN[j] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/IRIS/STATION/' + 'Input_Syn_BHN', 'a')
					syn = dic_BHN[j]['Network'] + ' , ' + dic_BHN[j]['Station'] + ' , ' + \
						dic_BHN[j]['Location'] + ' , ' + dic_BHN[j]['Channel'] + ' , ' + dic_BHN[j]['Latitude'] + \
						' , ' + dic_BHN[j]['Longitude'] + ' , ' + dic_BHN[j]['Elevation'] + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Networks_iris_BHN[i][j][0] +	'.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Networks_iris_BHN[i][j][0] +	'.' + Networks_iris_BHN[i][j][1] + \
						'.' +Networks_iris_BHN[i][j][2] + '.' + 'BHN'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Networks_iris_BHN[i][j][0] + \
						'.' + Networks_iris_BHN[i][j][1] + '.' + \
						Networks_iris_BHN[i][j][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHN', 'a')
		pickle.dump(dic_BHN, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'IRIS-Saved stations (BHN) for event' + '-' + str(i) + ': ' + str(len(dic_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		
				
		
		dic_BHZ = {}		
				
		if input['BHZ'] == 'Y':
			
			for j in range(0, len_req_iris_BHZ):
			
				print '------------------'
				print 'IRIS-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHZ'
				try:
					
					client_iris = Client_iris()
					
					# BHZ
					dummy = 'Waveform'
					
					client_iris.saveWaveform(Address_events + '/' + events[i]['event_id'] +\
						'/IRIS/' + Networks_iris_BHZ[i][j][0] +	'.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ', Networks_iris_BHZ[i][j][0], Networks_iris_BHZ[i][j][1], \
						Networks_iris_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Networks_iris_BHZ[i][j][0] + '.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"  
					
					dummy = 'Response'
					
					client_iris.saveResponse(Address_events + '/' +	events[i]['event_id'] + \
						'/IRIS/RESP/' + 'RESP' + '.' + Networks_iris_BHZ[i][j][0] +	'.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ', Networks_iris_BHZ[i][j][0], Networks_iris_BHZ[i][j][1], \
						Networks_iris_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Response for: " + Networks_iris_BHZ[i][j][0] + '.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
					
					'''
					dummy = 'sacpz'
					
					import ipdb; ipdb.set_trace()
					
					sacpz = client_iris.sacpz(network=Networks_iris_BHZ[i][j][0], \
						station=Networks_iris_BHZ[i][j][1], location=Networks_iris_BHZ[i][j][2], \
						channel="BHZ", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'availability'
					
					avail = client_iris.availability(network=Networks_iris_BHZ[i][j][0], \
						station=Networks_iris_BHZ[i][j][1], location=Networks_iris_BHZ[i][j][2], \
						channel="BHZ", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'], output = 'xml')
					
					
					xml_doc = etree.fromstring(avail)
							
					#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
					#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
					Sta_net_code = xml_doc.xpath('/StaMessage/Station')[0].get('net_code')
					Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[0].get('sta_code')
					Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[0].text
					Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[0].text
					Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[0].text
					Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('loc_code')
					Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('chan_code')
					#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
					#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
					#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
					#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
					#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
					#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
					#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
					#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
					dic_BHZ[j] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/IRIS/STATION/' + 'Input_Syn_BHZ', 'a')
					syn = dic_BHZ[j]['Network'] + ' , ' + dic_BHZ[j]['Station'] + ' , ' + \
						dic_BHZ[j]['Location'] + ' , ' + dic_BHZ[j]['Channel'] + ' , ' + dic_BHZ[j]['Latitude'] + \
						' , ' + dic_BHZ[j]['Longitude'] + ' , ' + dic_BHZ[j]['Elevation'] + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Networks_iris_BHZ[i][j][0] +	'.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Networks_iris_BHZ[i][j][0] +	'.' + Networks_iris_BHZ[i][j][1] + \
						'.' +Networks_iris_BHZ[i][j][2] + '.' + 'BHZ'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Networks_iris_BHZ[i][j][0] + \
						'.' + Networks_iris_BHZ[i][j][1] + '.' + \
						Networks_iris_BHZ[i][j][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHZ', 'a')
		pickle.dump(dic_BHZ, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'IRIS-Saved stations (BHZ) for event' + '-' + str(i) + ': ' + str(len(dic_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		
	
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
	
	
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
		Report.writelines('----------------------------------' + '\n')
		rep1 = "Time for getting and saving Waveforms from IRIS: " + str(t_wave) + '\n'
		Report.writelines(rep1)
		Report.writelines('----------------------------------' + '\n' + '\n')
		Report.close()
	
		print "-------------------------------------------------"
		print 'IRIS is DONE'
		print "Time for getting and saving Waveforms from IRIS:"
		print t_wave
