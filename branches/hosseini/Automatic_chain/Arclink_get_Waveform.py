"""
Gets Waveforms, Response files and other information from ArcLink based on the requested events...
-----------------
Problems:
- Client_arclink(command_delay=0.1)
"""

from obspy.arclink import Client as Client_arclink
from datetime import datetime
import time
from obspy.arclink.client import ArcLinkException as ArcLinkException
import pickle


def Arclink_get_Waveform(input, Nets_Arc_req_BHE, \
	Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t):
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/Data/' + Period
	
	Event_file = open(Address_events + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/EXCEP/' + 'Exception_file_ARC', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Avail_ARC_Stations_BHE', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Avail_ARC_Stations_BHN', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Avail_ARC_Stations_BHZ', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Input_Syn_BHE', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Input_Syn_BHN', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Input_Syn_BHZ', 'w')
		Syn_file.close()
	
	t_wave_1 = datetime.now()
	
	for i in range(0, len_events):
		
		t_wave_1 = datetime.now()
		
		if input['TEST'] == 'Y':
			len_req_Arc_BHE = input['TEST_no']
			len_req_Arc_BHN = input['TEST_no']
			len_req_Arc_BHZ = input['TEST_no']

		else:	
			len_req_Arc_BHE = len(Nets_Arc_req_BHE[i]) 
			len_req_Arc_BHN = len(Nets_Arc_req_BHN[i]) 
			len_req_Arc_BHZ = len(Nets_Arc_req_BHZ[i]) 		
		
		
		inv_BHE = {}
		
		if input['BHE'] == 'Y':
			
			for j in range(0, len_req_Arc_BHE):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHE'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHE
					dummy = 'Waveform'
					
					client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
						Nets_Arc_req_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"  
					
					
					dummy = 'Response'
					
					client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
						Nets_Arc_req_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
					
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')	
					'''	
					
					print "Saving Response for: " + Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
						
					
					dummy = 'Inventory'
					
					inv_BHE[j] = client_arclink.getInventory(Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
						Nets_Arc_req_BHE[i][j][2], 'BHE')
					
					dum = Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1]
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/STATION/' + 'Input_Syn_BHE', 'a')
					syn = Nets_Arc_req_BHE[i][j][0] + ' , ' + Nets_Arc_req_BHE[i][j][1] + ' , ' + \
						Nets_Arc_req_BHE[i][j][2] + ' , ' + Nets_Arc_req_BHE[i][j][3] + ' , ' + str(inv_BHE[j][dum]['latitude']) + \
						' , ' + str(inv_BHE[j][dum]['longitude']) + ' , ' + str(inv_BHE[j][dum]['elevation']) + ' , ' + \
						str(inv_BHE[j][dum]['depth']) + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + \
						'.' +Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHE[i][j][0] + \
						'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Avail_ARC_Stations_BHE', 'a')
		pickle.dump(inv_BHE, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		
		
		
		inv_BHN = {}
		
		if input['BHN'] == 'Y':
			
			for j in range(0, len_req_Arc_BHN):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHN'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHN
					dummy = 'Waveform'
					
					client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
						Nets_Arc_req_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"  
					
					
					dummy = 'Response'
					
					client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
						Nets_Arc_req_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
										
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
					'''
					
										
					print "Saving Response for: " + Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
					
					
					dummy = 'Inventory'
					
					inv_BHN[j] = client_arclink.getInventory(Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
						Nets_Arc_req_BHN[i][j][2], 'BHN')
					
					dum = Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1]
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/STATION/' + 'Input_Syn_BHN', 'a')
					syn = Nets_Arc_req_BHN[i][j][0] + ' , ' + Nets_Arc_req_BHN[i][j][1] + ' , ' + \
						Nets_Arc_req_BHN[i][j][2] + ' , ' + Nets_Arc_req_BHN[i][j][3] + ' , ' + str(inv_BHN[j][dum]['latitude']) + \
						' , ' + str(inv_BHN[j][dum]['longitude']) + ' , ' + str(inv_BHN[j][dum]['elevation']) + ' , ' + \
						str(inv_BHN[j][dum]['depth']) + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()					
					
					print "Saving Station  for: " + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + \
						'.' +Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHN[i][j][0] + \
						'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Avail_ARC_Stations_BHN', 'a')
		pickle.dump(inv_BHN, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHN) for event' + '-' + str(i) + ': ' + str(len(inv_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		

		inv_BHZ = {}
		
		if input['BHZ'] == 'Y':
			
			for j in range(0, len_req_Arc_BHZ):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i+1) + '-' + str(j) + '-BHZ'
				
				try:
					
					client_arclink = Client_arclink(command_delay=0.1)
					
					# BHZ
					dummy = 'Waveform'
					
					client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
						Nets_Arc_req_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"  
					
					
					dummy = 'Response'
					
					client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
						Nets_Arc_req_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
										
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
					'''
					
					print "Saving Response for: " + Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
						
					
					
					dummy = 'Inventory'
					
					inv_BHZ[j] = client_arclink.getInventory(Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
						Nets_Arc_req_BHZ[i][j][2], 'BHZ')
					
					dum = Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1]
					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/STATION/' + 'Input_Syn_BHZ', 'a')
					syn = Nets_Arc_req_BHZ[i][j][0] + ' , ' + Nets_Arc_req_BHZ[i][j][1] + ' , ' + \
						Nets_Arc_req_BHZ[i][j][2] + ' , ' + Nets_Arc_req_BHZ[i][j][3] + ' , ' + str(inv_BHZ[j][dum]['latitude']) + \
						' , ' + str(inv_BHZ[j][dum]['longitude']) + ' , ' + str(inv_BHZ[j][dum]['elevation']) + ' , ' + \
						str(inv_BHZ[j][dum]['depth']) + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
						
					print "Saving Station  for: " + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
					
					client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + \
						'.' +Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHZ[i][j][0] + \
						'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Avail_ARC_Stations_BHZ', 'a')
		pickle.dump(inv_BHZ, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
		rep1 = 'ArcLink-Saved stations (BHZ) for event' + '-' + str(i) + ': ' + str(len(inv_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	
	
	
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
		Report.writelines('----------------------------------' + '\n')
		rep1 = "Time for getting and saving Waveforms from ArcLink: " + str(t_wave) + '\n'
		Report.writelines(rep1)
		Report.writelines('----------------------------------' + '\n' + '\n')
		Report.close()
		
		print "-------------------------------------------------"
		print 'ArcLink is DONE'
		print "Time for getting and saving Waveforms from ArcLink:"
		print t_wave
