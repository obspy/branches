"""
Updating the station folders from IRIS web-service
Attention: This module update all station folders for all events in one directory.
-----------------
Problems:
- Exception_file_IRIS_update OR Exception_file_IRIS?
"""


from obspy.core import read
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pickle
from obspy.iris import Client as Client_iris
from datetime import datetime
from lxml import etree
from nodes_update import *


def update_IRIS(input):
		
	t_update_1 = datetime.now()
	
	Address_data = input['Address'] + '/Data'
	
	ls_period = os.listdir(Address_data)
	
	pre_ls_event = []
	for i in range(0, len(ls_period)):
		pre_ls_event.append(Address_data + '/' + ls_period[i])	
	
	pre_ls_event = nodes_update(input, pre_ls_event)
	
	for i in range(0, len(pre_ls_event)):
		print 'Updating for: ' + '\n' + str(pre_ls_event[i])
	print '*********************'
	
	ls_event_file = []
	for i in pre_ls_event:
		ls_event_file.append(os.listdir(i))
	
	ls_event = []
	
	for i in range(0, len(ls_event_file)):
		for j in range(0, len(ls_event_file[i])):
			if ls_event_file[i][j] != 'list_event':
				if ls_event_file[i][j] != 'EVENT':
					ls_event.append(pre_ls_event[0] + '/' + ls_event_file[i][j])
					print ls_event_file[i][j]
	
	add_IRIS_events = []
	for i in pre_ls_event:
		add_IRIS_events.append(i + '/list_event')
		
	events_all = []
	
	for i in add_IRIS_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	
	events_all_file = []
	
	for l in range(0, len(events_all)):
		events = pickle.load(events_all[l])
		for j in events:
			events_all_file.append(j)
	
	for l in range(0, len(ls_event)):

		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/All_IRIS_Stations_BHE', 'r')
		All_IRIS_Stations_BHE = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/All_IRIS_Stations_BHN', 'r')
		All_IRIS_Stations_BHN = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/All_IRIS_Stations_BHZ', 'r')
		All_IRIS_Stations_BHZ = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		for i in range(0, len(All_IRIS_Stations_BHE)):
			All_IRIS_Stations_BHE[i] = [All_IRIS_Stations_BHE[i][0], All_IRIS_Stations_BHE[i][1], \
				All_IRIS_Stations_BHE[i][2], All_IRIS_Stations_BHE[i][3]]
				
		for i in range(0, len(All_IRIS_Stations_BHN)):
			All_IRIS_Stations_BHN[i] = [All_IRIS_Stations_BHN[i][0], All_IRIS_Stations_BHN[i][1], \
				All_IRIS_Stations_BHN[i][2], All_IRIS_Stations_BHN[i][3]]
		
		for i in range(0, len(All_IRIS_Stations_BHZ)):
			All_IRIS_Stations_BHZ[i] = [All_IRIS_Stations_BHZ[i][0], All_IRIS_Stations_BHZ[i][1], \
				All_IRIS_Stations_BHZ[i][2], All_IRIS_Stations_BHZ[i][3]]
			
		'''
		upfile = open(ls_event[l] + '/IRIS/STATION/' + 'UPDATE', 'w')
		upfile.writelines('\n' + ls_event[l].split('/')[-1] + '\n')
		upfile.writelines('----------------------------IRIS----------------------------'+ '\n')
		upfile.writelines('----------------------------UPDATED----------------------------'+ '\n')
		upfile.close()
		'''	
		List_IRIS_BHE = []
		List_IRIS_BHN = []
		List_IRIS_BHZ = []
		
					
		List_IRIS_BHE.append(glob.glob(ls_event[l] + '/IRIS/' + '*.BHE'))
		List_IRIS_BHN.append(glob.glob(ls_event[l] + '/IRIS/' + '*.BHN'))
		List_IRIS_BHZ.append(glob.glob(ls_event[l] + '/IRIS/' + '*.BHZ'))

		List_IRIS_BHE = sorted(List_IRIS_BHE)
		List_IRIS_BHN = sorted(List_IRIS_BHN)
		List_IRIS_BHZ = sorted(List_IRIS_BHZ)
		
		pre_Sta_BHE = []
		pre_Sta_BHN = []
		pre_Sta_BHZ = []
		
		Sta_BHE = []
		Sta_BHN = []
		Sta_BHZ = []
			
		for i in range(0, len(List_IRIS_BHE[0])):
			try:
				st = read(List_IRIS_BHE[0][i])
				sta_BHE = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHE.append(sta_BHE)
			
			except Exception, e:	
					
				print 'STREAM' + '---'
				'''	
				Exception_file = open(Address + '/IRIS/EXCEP/' + 'Exception_file_IRIS_update', 'a')
				ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
					Stas_req_BHE[i][2] + '.' + 'BHE' +	'---' + str(e) + '\n'
							
				Exception_file.writelines(ee)
				Exception_file.close()
				'''
				print e
				
		for i in range(0, len(List_IRIS_BHN[0])):
			try:
				st = read(List_IRIS_BHN[0][i])
				sta_BHN = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHN.append(sta_BHN)
			
			except Exception, e:					
				print 'STREAM' + '---'
				print e
		
		for i in range(0, len(List_IRIS_BHZ[0])):
			try:
				st = read(List_IRIS_BHZ[0][i])
				sta_BHZ = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHZ.append(sta_BHZ)
			
			except Exception, e:					
				print 'STREAM' + '---'
				print e
			
		Sta_BHE.append(pre_Sta_BHE)
		Sta_BHN.append(pre_Sta_BHN)
		Sta_BHZ.append(pre_Sta_BHZ)
		
		for i in range(0, len(All_IRIS_Stations_BHE)):
			if All_IRIS_Stations_BHE[i] != []:
				if All_IRIS_Stations_BHE[i][2] == '--':
					All_IRIS_Stations_BHE[i][2] = ''
		
		for i in range(0, len(All_IRIS_Stations_BHN)):
			if All_IRIS_Stations_BHN[i] != []:
				if All_IRIS_Stations_BHN[i][2] == '--':
					All_IRIS_Stations_BHN[i][2] = ''
				
		for i in range(0, len(All_IRIS_Stations_BHZ)):
			if All_IRIS_Stations_BHZ[i] != []:
				if All_IRIS_Stations_BHZ[i][2] == '--':
					All_IRIS_Stations_BHZ[i][2] = ''	 		
 		
 		common_BHE = []
 		
 		for i in range(0, len(All_IRIS_Stations_BHE)):
 			for j in range(0, len(Sta_BHE[0])):
 				if All_IRIS_Stations_BHE[i] == Sta_BHE[0][j]:
 					common_BHE.append(All_IRIS_Stations_BHE[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHE)):
 			for j in range(0, len(All_IRIS_Stations_BHE)):
 				if common_BHE[i] == All_IRIS_Stations_BHE[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_IRIS_Stations_BHE[i] = []
 		
 		
 		Stas_req_BHE = []
 		
 		for i in All_IRIS_Stations_BHE:
 			if i != []:
 				Stas_req_BHE.append(i)
 				
 		
 		common_BHN = []
 		
 		for i in range(0, len(All_IRIS_Stations_BHN)):
 			for j in range(0, len(Sta_BHN[0])):
 				if All_IRIS_Stations_BHN[i] == Sta_BHN[0][j]:
 					common_BHN.append(All_IRIS_Stations_BHN[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHN)):
 			for j in range(0, len(All_IRIS_Stations_BHN)):
 				if common_BHN[i] == All_IRIS_Stations_BHN[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_IRIS_Stations_BHN[i] = []
 		
 		
 		Stas_req_BHN = []
 		
 		for i in All_IRIS_Stations_BHN:
 			if i != []:
 				Stas_req_BHN.append(i)
 				
 				
 		common_BHZ = []
 		
 		for i in range(0, len(All_IRIS_Stations_BHZ)):
 			for j in range(0, len(Sta_BHZ[0])):
 				if All_IRIS_Stations_BHZ[i] == Sta_BHZ[0][j]:
 					common_BHZ.append(All_IRIS_Stations_BHZ[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHZ)):
 			for j in range(0, len(All_IRIS_Stations_BHZ)):
 				if common_BHZ[i] == All_IRIS_Stations_BHZ[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_IRIS_Stations_BHZ[i] = []
 		
 		
 		Stas_req_BHZ = []
 		
 		for i in All_IRIS_Stations_BHZ:
 			if i != []:
 				Stas_req_BHZ.append(i)
 		
 		
 		for i in range(0, len(Stas_req_BHE)):
 			if Stas_req_BHE[i][2] == '':
 				Stas_req_BHE[i][2] = '--'
 		
 		for i in range(0, len(Stas_req_BHN)):
 			if Stas_req_BHN[i][2] == '':
 				Stas_req_BHN[i][2] = '--'
 		
 		for i in range(0, len(Stas_req_BHZ)):
 			if Stas_req_BHZ[i][2] == '':
 				Stas_req_BHZ[i][2] = '--'		
 		
 		
 		for i in events_all_file:
			if i['event_id'] == ls_event[l].split('/')[-1]:
				event_id = i['event_id']
				Address = ls_event[l]
				t1 = i['datetime']-input['t_before']
				t2 = i['datetime']+input['t_after']
				
		
		
		Exception_file = open(Address + '/' + '/IRIS/EXCEP/' + 'Exception_file_IRIS_update', 'w')
		Exception_file.writelines('\n' + event_id + '\n')
		Exception_file.writelines('----------------------------UPDATE - IRIS----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		
		
		dic_BHE = {}		
				
		if input['BHE'] == 'Y':
					
			for i in range(0, len(Stas_req_BHE)):			
				
				print '------------------'
				
				try:					
			
					client_iris = Client_iris()
							
					# BHE
					dummy = 'UPDATE-Waveform'
							
					client_iris.saveWaveform(Address + '/IRIS/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE', t1, t2)
							
					print "UPDATE - Saving Waveform for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"  
							
					dummy = 'UPDATE-Response'
							
					client_iris.saveResponse(Address + '/IRIS/RESP/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE', t1, t2)
							
					print "UPDATE - Saving Response for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHE[i][j][0], \
						station=Networks_iris_BHE[i][j][1], location=Networks_iris_BHE[i][j][2], \
						channel="BHE", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
							
					avail = client_iris.availability(network=Stas_req_BHE[i][0], \
						station=Stas_req_BHE[i][1], location=Stas_req_BHE[i][2], \
						channel="BHE", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					dic_BHE[j] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE'
					
					Exception_file = open(Address + '/IRIS/EXCEP/' + 'Exception_file_IRIS_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHE', 'a')
		pickle.dump(dic_BHE, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHE) for event' + '-' + str(l) + ': ' + str(len(dic_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
				
		for k in dic_BHE.keys():
			Syn_file = open(Address + '/IRIS/STATION/' + 'Input_Syn_BHE', 'a')
			syn = dic_BHE[k]['Network'] + ' , ' + dic_BHE[k]['Station'] + ' , ' + \
				dic_BHE[k]['Location'] + ' , ' + dic_BHE[k]['Channel'] + ' , ' + dic_BHE[k]['Latitude'] + \
				' , ' + dic_BHE[k]['Longitude'] + ' , ' + dic_BHE[k]['Elevation'] + '\n'
			Syn_file.writelines(syn)
			Syn_file.close()
						
				
		dic_BHN = {}		
				
		if input['BHN'] == 'Y':
					
			for i in range(0, len(Stas_req_BHN)):			
					
				print '------------------'
					
				try:					
			
					client_iris = Client_iris()
							
					# BHN
					dummy = 'UPDATE-Waveform'
							
					client_iris.saveWaveform(Address + '/IRIS/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN', t1, t2)
							
					print "UPDATE - Saving Waveform for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"  
							
					dummy = 'UPDATE-Response'
							
					client_iris.saveResponse(Address + '/IRIS/RESP/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN', t1, t2)
							
					print "UPDATE - Saving Response for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHN[i][j][0], \
						station=Networks_iris_BHN[i][j][1], location=Networks_iris_BHN[i][j][2], \
						channel="BHN", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
							
					avail = client_iris.availability(network=Stas_req_BHN[i][0], \
						station=Stas_req_BHN[i][1], location=Stas_req_BHN[i][2], \
						channel="BHN", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN'
					
					Exception_file = open(Address + '/IRIS/EXCEP/' + 'Exception_file_IRIS_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHN', 'a')
		pickle.dump(dic_BHN, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHN) for event' + '-' + str(l) + ': ' + str(len(dic_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()	
				
		for k in dic_BHN.keys():
			Syn_file = open(Address + '/IRIS/STATION/' + 'Input_Syn_BHN', 'a')
			syn = dic_BHN[k]['Network'] + ' , ' + dic_BHN[k]['Station'] + ' , ' + \
				dic_BHN[k]['Location'] + ' , ' + dic_BHN[k]['Channel'] + ' , ' + dic_BHN[k]['Latitude'] + \
				' , ' + dic_BHN[k]['Longitude'] + ' , ' + dic_BHN[k]['Elevation'] + '\n'
			Syn_file.writelines(syn)
			Syn_file.close()
					
					
		dic_BHZ = {}		
				
		if input['BHZ'] == 'Y':
					
			for i in range(0, len(Stas_req_BHZ)):			
					
				print '------------------'
					
				try:					
			
					client_iris = Client_iris()
							
					# BHZ
					dummy = 'UPDATE-Waveform'
							
					client_iris.saveWaveform(Address + '/IRIS/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ', t1, t2)
							
					print "UPDATE - Saving Waveform for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"  
							
					dummy = 'UPDATE-Response'
							
					client_iris.saveResponse(Address + '/IRIS/RESP/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ', t1, t2)
							
					print "UPDATE - Saving Response for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHZ[i][j][0], \
						station=Networks_iris_BHZ[i][j][1], location=Networks_iris_BHZ[i][j][2], \
						channel="BHZ", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
							
					avail = client_iris.availability(network=Stas_req_BHZ[i][0], \
						station=Stas_req_BHZ[i][1], location=Stas_req_BHZ[i][2], \
						channel="BHZ", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ'
					
					Exception_file = open(Address + '/IRIS/EXCEP/' + 'Exception_file_IRIS_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/STATION/' + 'Avail_IRIS_Stations_BHZ', 'a')
		pickle.dump(dic_BHZ, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/STATION/' + 'Report_station', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHZ) for event' + '-' + str(l) + ': ' + str(len(dic_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	
				
		for k in dic_BHZ.keys():
			Syn_file = open(Address + '/IRIS/STATION/' + 'Input_Syn_BHZ', 'a')
			syn = dic_BHZ[k]['Network'] + ' , ' + dic_BHZ[k]['Station'] + ' , ' + \
				dic_BHZ[k]['Location'] + ' , ' + dic_BHZ[k]['Channel'] + ' , ' + dic_BHZ[k]['Latitude'] + \
				' , ' + dic_BHZ[k]['Longitude'] + ' , ' + dic_BHZ[k]['Elevation'] + '\n'
			Syn_file.writelines(syn)
			Syn_file.close()
		
		
			
	t_update_2 = datetime.now()
		
	t_update = t_update_2 - t_update_1
		
	print 'Time for Updating: (IRIS)'
	print t_update
