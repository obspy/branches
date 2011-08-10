"""
Updating the station folders from ArcLink
Attention: This module update all station folders for all events in one directory.
-----------------
Problems:
- Exception_file_ARC_update OR Exception_file_ARC?
"""


from obspy.arclink import Client as Client_arclink
from datetime import datetime
import time
from obspy.arclink.client import ArcLinkException as ArcLinkException
import pickle
import os
import glob
from obspy.core import read
import numpy as np
from nodes_update import *

def update_ARC(input):
		
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
	
	add_ARC_events = []
	for i in pre_ls_event:
		add_ARC_events.append(i + '/list_event')
		
	events_all = []
	
	for i in add_ARC_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	
	events_all_file = []
	
	for l in range(0, len(events_all)):
		events = pickle.load(events_all[l])
		for j in events:
			events_all_file.append(j)
	
	for l in range(0, len(ls_event)):
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/All_ARC_Stations_BHE', 'r')
		All_ARC_Stations_BHE = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/All_ARC_Stations_BHN', 'r')
		All_ARC_Stations_BHN = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/All_ARC_Stations_BHZ', 'r')
		All_ARC_Stations_BHZ = pickle.load(ls_stas_open)
		ls_stas_open.close()
		'''
		upfile = open(ls_event[l] + '/ARC/STATION/' + 'UPDATE', 'w')
		upfile.writelines('\n' + ls_event[l].split('/')[-1] + '\n')
		upfile.writelines('----------------------------ARC----------------------------'+ '\n')
		upfile.writelines('----------------------------UPDATED----------------------------'+ '\n')
		upfile.close()
		'''
		List_ARC_BHE = []
		List_ARC_BHN = []
		List_ARC_BHZ = []
		
					
		List_ARC_BHE.append(glob.glob(ls_event[l] + '/ARC/' + '*.BHE'))
		List_ARC_BHN.append(glob.glob(ls_event[l] + '/ARC/' + '*.BHN'))
		List_ARC_BHZ.append(glob.glob(ls_event[l] + '/ARC/' + '*.BHZ'))

		List_ARC_BHE = sorted(List_ARC_BHE)
		List_ARC_BHN = sorted(List_ARC_BHN)
		List_ARC_BHZ = sorted(List_ARC_BHZ)
		
		#------------------------------------------------------------------------------------
		exception_arc = open(ls_event[l] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'r')
		excepts = exception_arc.readlines()
		
		for i in range(0, len(excepts)):
   			excepts[i] = excepts[i].split('---')
   		
   		Access_denied = []
   		No_data = []
   		
   		for i in range(2, len(excepts)):
			if excepts[i][3] == 'DENIED access denied for user ObsPy\n':
				Access_denied.append(excepts[i][2])
				
			if excepts[i][3] == 'No data available\n':
				No_data.append(excepts[i][2])
				
		
		for i in range(0, len(Access_denied)):
			Access_denied[i] = Access_denied[i].split('.')
		
		
		for i in range(0, len(No_data)):
			No_data[i] = No_data[i].split('.')
		
		#------------------------------------------------------------------------------------
		pre_Sta_BHE = []
		pre_Sta_BHN = []
		pre_Sta_BHZ = []
		
		Sta_BHE = []
		Sta_BHN = []
		Sta_BHZ = []
			
		for i in range(0, len(List_ARC_BHE[0])):
			try:
				st = read(List_ARC_BHE[0][i])
				sta_BHE = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHE.append(sta_BHE)
			
			except Exception, e:	
					
				print 'STREAM' + '---'
				'''	
				Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')
				ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
					Stas_req_BHE[i][2] + '.' + 'BHE' +	'---' + str(e) + '\n'
							
				Exception_file.writelines(ee)
				Exception_file.close()
				'''
				print e
				
		for i in range(0, len(List_ARC_BHN[0])):
			try:
				st = read(List_ARC_BHN[0][i])
				sta_BHN = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHN.append(sta_BHN)
			
			except Exception, e:					
				print 'STREAM' + '---'
				print e
		
		for i in range(0, len(List_ARC_BHZ[0])):
			try:
				st = read(List_ARC_BHZ[0][i])
				sta_BHZ = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				pre_Sta_BHZ.append(sta_BHZ)
			
			except Exception, e:					
				print 'STREAM' + '---'
				print e
		
		Sta_BHE.append(pre_Sta_BHE)
		Sta_BHN.append(pre_Sta_BHN)
		Sta_BHZ.append(pre_Sta_BHZ)
 		
 		common_BHE = []
 		
 		for i in range(0, len(All_ARC_Stations_BHE)):
 			for j in range(0, len(Sta_BHE[0])):
 				if All_ARC_Stations_BHE[i] == Sta_BHE[0][j]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHE[i] == Access_denied[m]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHE[i] == No_data[n]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHE)):
 			for j in range(0, len(All_ARC_Stations_BHE)):
 				if common_BHE[i] == All_ARC_Stations_BHE[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHE[i] = []
 		
 		
 		Stas_req_BHE = []
 		
 		for i in All_ARC_Stations_BHE:
 			if i != []:
 				Stas_req_BHE.append(i)
 				
 		
 		common_BHN = []
 		
 		for i in range(0, len(All_ARC_Stations_BHN)):
 			for j in range(0, len(Sta_BHN[0])):
 				if All_ARC_Stations_BHN[i] == Sta_BHN[0][j]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHN[i] == Access_denied[m]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHN[i] == No_data[n]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHN)):
 			for j in range(0, len(All_ARC_Stations_BHN)):
 				if common_BHN[i] == All_ARC_Stations_BHN[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHN[i] = []
 		
 		
 		Stas_req_BHN = []
 		
 		for i in All_ARC_Stations_BHN:
 			if i != []:
 				Stas_req_BHN.append(i)
 				
 				
 		common_BHZ = []
 		
 		for i in range(0, len(All_ARC_Stations_BHZ)):
 			for j in range(0, len(Sta_BHZ[0])):
 				if All_ARC_Stations_BHZ[i] == Sta_BHZ[0][j]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHZ[i] == Access_denied[m]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHZ[i] == No_data[n]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 				
 		num_j = []
 		for i in range(0, len(common_BHZ)):
 			for j in range(0, len(All_ARC_Stations_BHZ)):
 				if common_BHZ[i] == All_ARC_Stations_BHZ[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHZ[i] = []
 		
 		
 		Stas_req_BHZ = []
 		
 		for i in All_ARC_Stations_BHZ:
 			if i != []:
 				Stas_req_BHZ.append(i)
 		
 		for i in events_all_file:
			if i['event_id'] == ls_event[l].split('/')[-1]:
				event_id = i['event_id']
				Address = ls_event[l]
				t1 = i['datetime']-input['t_before']
				t2 = i['datetime']+input['t_after']
				
		
		
		Exception_file = open(Address + '/' + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'w')
		Exception_file.writelines('\n' + event_id + '\n')
		Exception_file.writelines('----------------------------UPDATE - ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		
		
		#import ipdb; ipdb.set_trace()
		inv_BHE = {}
		
		if input['BHE'] == 'Y':
			
			for i in range(0, len(Stas_req_BHE)):
				
				print '------------------'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHE
					dummy = 'UPDATE-Waveform'
					
					client_arclink.saveWaveform(Address + '/ARC/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE', t1, t2)
					
					print "UPDATE - Saving Waveform for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"  
										
					dummy = 'UPDATE-Response'
					
					client_arclink.saveResponse(Address + '/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE', t1, t2)
					
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE')	
					'''	
					
					print "UPDATE - Saving Response for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
						
					
					dummy = 'UPDATE-Inventory'
					
					inv_BHE[j] = client_arclink.getInventory(Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE')
										
					print "UPDATE - Saving Station  for: " + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + \
						'.' +Stas_req_BHE[i][2] + '.' + 'BHE'
					
					Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHE[i][0] + \
						'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/STATION/' + 'Avail_ARC_Stations_BHE', 'a')
		pickle.dump(inv_BHE, Station_file)
		Station_file.close()
		
		
		Report = open(Address + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		
		for k in inv_BHE.keys():
				
			try:
					
				dum = Stas_req_BHE[int(k)][0] + '.' + Stas_req_BHE[int(k)][1]
				Syn_file = open(Address + '/ARC/STATION/' + 'Input_Syn_BHE', 'a')
				syn = Stas_req_BHE[int(k)][0] + ' , ' + Stas_req_BHE[int(k)][1] + ' , ' + \
					Stas_req_BHE[int(k)][2] + ' , ' + Stas_req_BHE[int(k)][3] + ' , ' + str(inv_BHE[int(k)][dum]['latitude']) + \
					' , ' + str(inv_BHE[int(k)][dum]['longitude']) + ' , ' + str(inv_BHE[int(k)][dum]['elevation']) + ' , ' + \
				str(inv_BHE[int(k)][dum]['depth']) + '\n'
				Syn_file.writelines(syn)
				Syn_file.close()
				
			except Exception, e:	
					
				print 'SYNTHETIC' + '---' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + \
					'.' +Stas_req_BHE[i][2] + '.' + 'BHE'
					
				Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')
						
				ee = 'SYNTHETIC' + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHE[i][0] + \
					'.' + Stas_req_BHE[i][1] + '.' + \
					Stas_req_BHE[i][2] + '.' + 'BHE' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
				
				
		
		inv_BHN = {}
		
		if input['BHN'] == 'Y':
			
			for i in range(0, len(Stas_req_BHN)):
				
				print '------------------'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHN
					dummy = 'UPDATE-Waveform'
					
					client_arclink.saveWaveform(Address + '/ARC/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN', t1, t2)
					
					print "UPDATE - Saving Waveform for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"  
										
					dummy = 'UPDATE-Response'
					
					client_arclink.saveResponse(Address + '/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN', t1, t2)
					
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN')	
					'''	
					
					print "UPDATE - Saving Response for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
						
					
					dummy = 'UPDATE-Inventory'
					
					inv_BHN[j] = client_arclink.getInventory(Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN')
										
					print "UPDATE - Saving Station  for: " + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + \
						'.' +Stas_req_BHN[i][2] + '.' + 'BHN'
					
					Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHN[i][0] + \
						'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/STATION/' + 'Avail_ARC_Stations_BHN', 'a')
		pickle.dump(inv_BHN, Station_file)
		Station_file.close()
			
			
		Report = open(Address + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHN) for event' + '-' + str(i) + ': ' + str(len(inv_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()	
			
		for k in inv_BHN.keys():
				
			try:
					
				dum = Stas_req_BHN[int(k)][0] + '.' + Stas_req_BHN[int(k)][1]
				Syn_file = open(Address + '/ARC/STATION/' + 'Input_Syn_BHN', 'a')
				syn = Stas_req_BHN[int(k)][0] + ' , ' + Stas_req_BHN[int(k)][1] + ' , ' + \
					Stas_req_BHN[int(k)][2] + ' , ' + Stas_req_BHN[int(k)][3] + ' , ' + str(inv_BHN[int(k)][dum]['latitude']) + \
					' , ' + str(inv_BHN[int(k)][dum]['longitude']) + ' , ' + str(inv_BHN[int(k)][dum]['elevation']) + ' , ' + \
					str(inv_BHN[int(k)][dum]['depth']) + '\n'
				Syn_file.writelines(syn)
				Syn_file.close()
				
			except Exception, e:	
						
				print 'SYNTHETIC' + '---' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + \
					'.' +Stas_req_BHN[i][2] + '.' + 'BHN'
				
				Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')
						
				ee = 'SYNTHETIC' + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHN[i][0] + \
					'.' + Stas_req_BHN[i][1] + '.' + \
					Stas_req_BHN[i][2] + '.' + 'BHN' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
				
				
		
		inv_BHZ = {}
		
		if input['BHZ'] == 'Y':
			
			for i in range(0, len(Stas_req_BHZ)):
				
				print '------------------'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHZ
					dummy = 'UPDATE-Waveform'
					
					client_arclink.saveWaveform(Address + '/ARC/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ', t1, t2)
					
					print "UPDATE - Saving Waveform for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"  
										
					dummy = 'UPDATE-Response'
					
					client_arclink.saveResponse(Address + '/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ', t1, t2)
					
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ')	
					'''	
					
					print "UPDATE - Saving Response for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
						
					
					dummy = 'UPDATE-Inventory'
					
					inv_BHZ[j] = client_arclink.getInventory(Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ')
										
					print "UPDATE - Saving Station  for: " + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + \
						'.' +Stas_req_BHZ[i][2] + '.' + 'BHZ'
					
					Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHZ[i][0] + \
						'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/STATION/' + 'Avail_ARC_Stations_BHZ', 'a')
		pickle.dump(inv_BHZ, Station_file)
		Station_file.close()
			
			
		Report = open(Address + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHZ) for event' + '-' + str(i) + ': ' + str(len(inv_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	
			
		for k in inv_BHZ.keys():
				
			try:
					
				dum = Stas_req_BHZ[int(k)][0] + '.' + Stas_req_BHZ[int(k)][1]
				Syn_file = open(Address + '/ARC/STATION/' + 'Input_Syn_BHZ', 'a')
				syn = Stas_req_BHZ[int(k)][0] + ' , ' + Stas_req_BHZ[int(k)][1] + ' , ' + \
					Stas_req_BHZ[int(k)][2] + ' , ' + Stas_req_BHZ[int(k)][3] + ' , ' + str(inv_BHZ[int(k)][dum]['latitude']) + \
					' , ' + str(inv_BHZ[int(k)][dum]['longitude']) + ' , ' + str(inv_BHZ[int(k)][dum]['elevation']) + ' , ' + \
					str(inv_BHZ[int(k)][dum]['depth']) + '\n'
				Syn_file.writelines(syn)
				Syn_file.close()
				
			except Exception, e:	
						
				print 'SYNTHETIC' + '---' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + \
					'.' +Stas_req_BHZ[i][2] + '.' + 'BHZ'
					
				Exception_file = open(Address + '/ARC/EXCEP/' + 'Exception_file_ARC_update', 'a')
						
				ee = 'SYNTHETIC' + '---' + str(i) + '-' + str(j) + '---' + Stas_req_BHZ[i][0] + \
					'.' + Stas_req_BHZ[i][1] + '.' + \
					Stas_req_BHZ[i][2] + '.' + 'BHZ' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
				
				
				
