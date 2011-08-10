"""
Gets one Waveform, Response file and other information from ArcLink based on the requested network, station, location, channel and events...
ATTENTION: In this case, you should exactly know the net, sta, loc, cha of your request. Wild-cards are not allowed!
-----------------
Problems:
- Client_arclink(command_delay=0.1)
"""

from obspy.arclink import Client as Client_arclink
from datetime import datetime
import time
from obspy.arclink.client import ArcLinkException as ArcLinkException
import pickle
import os


def Arclink_get_Waveform_single(input, Address_events, len_events, events, Networks_ARC, t):
	
	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/RESP/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/EXCEP/')
		
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/EXCEP/' + 'Exception_file_ARC', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Avail_ARC_Stations', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Input_Syn', 'w')
		Syn_file.close()
	
	
	client_arclink = Client_arclink(command_delay=0.1)
	
	for i in range(0, len_events):
		
		t_wave_1 = datetime.now()
		
		print '------------------'
		print 'ArcLink-Event Number is:'
		print str(i+1)
		
		inv = {}
				
		try:
				
			client_arclink = Client_arclink(command_delay=0.1)
					
			dummy = 'Waveform'
				
			client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/' + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3], Networks_ARC[0], Networks_ARC[1], \
				Networks_ARC[2], Networks_ARC[3], t[i]-input['t_before'], t[i]+input['t_after'])
					
			print "Saving Waveform for: " + Networks_ARC[0] + '.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"  
					
					
			dummy = 'Response'
					
			client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/RESP/' + 'RESP' + '.' + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3], Networks_ARC[0], Networks_ARC[1], \
				Networks_ARC[2], Networks_ARC[3], t[i]-input['t_before'], t[i]+input['t_after'])
										
			print "Saving Response for: " + Networks_ARC[0] + '.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"
						
					
			dummy = 'Inventory'
					
			inv = client_arclink.getInventory(Networks_ARC[0], Networks_ARC[1], \
				Networks_ARC[2], Networks_ARC[3])
										
			print "Saving Station  for: " + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"
				
		except Exception, e:	
					
			print dummy + '---' + Networks_ARC[0] +	'.' + Networks_ARC[1] + \
				'.' +Networks_ARC[2] + '.' + Networks_ARC[3]
					
			Exception_file = open(Address_events + '/' + \
				events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

			ee = dummy + '---' + str(i) + '---' + Networks_ARC[0] + \
				'.' + Networks_ARC[1] + '.' + Networks_ARC[2] + '.' + Networks_ARC[3] + \
				'---' + str(e) + '\n'
					
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
		
		
		client_arclink.close()
		
		if len(inv) == 0:
			print 'No waveform Available'
		
		else:
			
			Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Avail_ARC_Stations_BHE', 'a')
			pickle.dump(inv, Station_file)
			Station_file.close()
			
			
			Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
			rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv)) + '\n'
			Report.writelines(rep1)
			Report.close()	
			
			dum = Networks_ARC[0] + '.' + Networks_ARC[1]
			Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/STATION/' + 'Input_Syn', 'a')
			
			syn = Networks_ARC[0] + '  ' + Networks_ARC[1] + '  ' + \
				Networks_ARC[2] + '  ' + Networks_ARC[3] + '  ' + str(inv[dum]['latitude']) + \
				'  ' + str(inv[dum]['longitude']) + '  ' + str(inv[dum]['elevation']) + '  ' + \
				str(inv[dum]['depth']) + '\n'
			
			Syn_file.writelines(syn)
			Syn_file.close()		
		
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
