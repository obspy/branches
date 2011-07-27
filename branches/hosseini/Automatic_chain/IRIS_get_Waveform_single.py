'''
Getting Waveform from IRIS web-service based on the desired events...
'''

from datetime import datetime
import time
import pickle
from obspy.iris import Client as Client_iris
import os
from lxml import etree


def IRIS_get_Waveform_single(input, Address_events, len_events, events, Networks_iris, t):
	
	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/RESP/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/EXCEP/')
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/EXCEP/' + 'Exception_file_IRIS', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------IRIS----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Avail_IRIS_Stations', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/STATION/' + 'Input_Syn', 'w')
		Syn_file.close()
		
	
	
	for i in range(0, len_events):
		
		t_wave_1 = datetime.now()		
		
		print '------------------'
		print 'IRIS-Event Number is:'
		print str(i+1)
		
		dic = {}		
				
		try:
					
			client_iris = Client_iris()
			
			dummy = 'Waveform'
			
			client_iris.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
				'/IRIS/' + Networks_iris[0] + '.' + Networks_iris[1] + '.' + Networks_iris[2] + \
				'.' + Networks_iris[3], Networks_iris[0], Networks_iris[1], Networks_iris[2], \
				Networks_iris[3], t[i]-input['t_before'], t[i]+input['t_after'])
			
			print "Saving Waveform for: " + Networks_iris[0] + '.' + Networks_iris[1] + '.' + \
				Networks_iris[2] + '.' + Networks_iris[3] + "  ---> DONE"  
			
			dummy = 'Response'
			
			client_iris.saveResponse(Address_events + '/' +	events[i]['event_id'] + \
				'/IRIS/RESP/' + 'RESP' + '.' + Networks_iris[0] +	'.' + Networks_iris[1] + '.' + \
				Networks_iris[2] + '.' + Networks_iris[3], Networks_iris[0], Networks_iris[1], \
				Networks_iris[2], Networks_iris[3], t[i]-input['t_before'], t[i]+input['t_after'])
			
			print "Saving Response for: " + Networks_iris[0] + '.' + Networks_iris[1] + '.' + \
				Networks_iris[2] + '.' + Networks_iris[3] + "  ---> DONE"
			
			'''
			dummy = 'sacpz'
					
			import ipdb; ipdb.set_trace()
			
			sacpz = client_iris.sacpz(network=Networks_iris[0], \
				station=Networks_iris[1], location=Networks_iris[2], \
				channel=Networks_iris[3], starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
			'''
			
			dummy = 'availability'
			
			avail = client_iris.availability(network=Networks_iris[0], \
				station=Networks_iris[1], location=Networks_iris[2], \
				channel=Networks_iris[3], starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'], output = 'xml')
			
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
			dic ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
				'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
				'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
			
			
			print "Saving Station  for: " + Networks_iris[0] +	'.' + Networks_iris[1] + '.' + \
				Networks_iris[2] + '.' + Networks_iris[3] + "  ---> DONE"
					
		except Exception, e:	
					
			print dummy + '---' + Networks_iris[0] +	'.' + Networks_iris[1] + \
				'.' +Networks_iris[2] + '.' + Networks_iris[3]
			
			Exception_file = open(Address_events + '/' + \
				events[i]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

			ee = dummy + '---' + str(i) + '---' + Networks_iris[0] + \
				'.' + Networks_iris[1] + '.' + \
				Networks_iris[2] + '.' + Networks_iris[3] + \
				'---' + str(e) + '\n'
					
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
		
		if len(dic) == 0:
			print 'No waveform Available'
		
		
		else:
			
			Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Avail_IRIS_Stations', 'a')
			pickle.dump(dic, Station_file)
			Station_file.close()
					
			Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/STATION/' + 'Report_station', 'a')
			rep1 = 'IRIS-Saved stations for event' + '-' + str(i) + ': ' + str(len(dic)) + '\n'
			Report.writelines(rep1)
			Report.close()	
			
			#import ipdb; ipdb.set_trace()
			
		
			Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/IRIS/STATION/' + 'Input_Syn', 'a')
			syn = dic['Network'] + '  ' + dic['Station'] + '  ' + \
				dic['Location'] + '  ' + dic['Channel'] + '  ' + dic['Latitude'] + \
				'  ' + dic['Longitude'] + '  ' + dic['Elevation'] + '\n'
			Syn_file.writelines(syn)
			Syn_file.close()
			
	
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
	
	
	
'''
Lat_temp.append([i, Networks_iris[i][str(j)]['Latitude']])
Lon_temp.append([i, Networks_iris[i][str(j)]['Longitude']])
name_temp.append([i, Networks_iris[i][str(j)]['Network'] + '.' + \
					Networks_iris[i][str(j)]['Station']])
Lat.append([i, Networks_iris[i][str(j)]['Latitude']])
Lon.append([i, Networks_iris[i][str(j)]['Longitude']])
name.append([i, Networks_iris[i][str(j)]['Network'] + '.' +Networks_iris[i][str(j)]['Station']])

				
Len_Lat_Lon.append(len(Lat_temp)) 
return Lat, Lon, name, Len_Lat_Lon
'''
	
