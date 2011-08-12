"""
Arclink: Returns available stations for all requested events
-----------------
Problems:
- ['BW', 'WETR', '', 'BH*']
- Client_arclink(command_delay=0.1)
"""

from obspy.arclink import Client as Client_arclink
from obspy.core import UTCDateTime
from datetime import datetime
import pickle
import time
import os
import shutil
import sys

client_arclink = Client_arclink(command_delay=0.1)

def Arclink_get_Network(input):
	
	t_arc_1 = datetime.now()


	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/Data/' + Period
	
	Event_file = open(Address_events + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	for i in range(0, len_events):
		if os.path.exists(Address_events + '/' + events[i]['event_id'] + '/ARC') == True:
			
			if raw_input('Folder for ARC -- requested Period (min/max) and Magnitude (min/max) exists in your directory.' + '\n\n' + \
			'You could either close the program and try updating your folder OR remove the tree, continue the program and download again.' + \
			'\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
				print '-------------------------------------------------------------'
				shutil.rmtree(Address_events + '/' + events[i]['event_id'] + '/ARC')

			else:
				print '-------------------------------------------------------------'
				print 'So...you decided to update your folder...Ciao'
				print '-------------------------------------------------------------'
				sys.exit()

	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/RESP/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/EXCEP/')
	
	print "-------------------------------------------------"
	print 'ArcLink-Folders are Created!'


	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/EXCEP/' + 'Exception_Availability', 'w')
		Report = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'Report_station', 'w')
		Exception_file.close()
		Report.close()
	
	
	t = []
	
	Networks_Arclink = []
	Nets_Arc_req_BHE = []
	Nets_Arc_req_BHN = []
	Nets_Arc_req_BHZ = []

	for i in range(0, len_events):
		
		t.append(UTCDateTime(events[i]['datetime']))
	
		try:
			
			Networks_Arclink.append(client_arclink.getNetworks(t[i]-10, t[i]+10))
			print 'ArcLink-Availability for event: ' + str(i) + '  --->' + 'DONE'

		except Exception, e:
				
			Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/EXCEP/' + 'Exception_Availability', 'a')
			ee = 'Event:' + str(i) + '---' + str(e) + '\n'
			
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
				
		nets_Arc_req_BHE=sorted([X for X in Networks_Arclink[i].keys() if ".BHE" in X])
		Nets_Arc_req_BHE.append(nets_Arc_req_BHE)	
		nets_Arc_req_BHN=sorted([X for X in Networks_Arclink[i].keys() if ".BHN" in X])
		Nets_Arc_req_BHN.append(nets_Arc_req_BHN)
		nets_Arc_req_BHZ=sorted([X for X in Networks_Arclink[i].keys() if ".BHZ" in X])
		Nets_Arc_req_BHZ.append(nets_Arc_req_BHZ)

	
		
	client_arclink.close()
	
	for i in range(0, len_events):
		len_req_Arc_BHE = len(Nets_Arc_req_BHE[i])
		for j in range(0, len_req_Arc_BHE):
			Nets_Arc_req_BHE[i][j] = Nets_Arc_req_BHE[i][j].split('.')

	for i in range(0, len_events):
		len_req_Arc_BHN = len(Nets_Arc_req_BHN[i])
		for j in range(0, len_req_Arc_BHN):
			Nets_Arc_req_BHN[i][j] = Nets_Arc_req_BHN[i][j].split('.')

	for i in range(0, len_events):
		len_req_Arc_BHZ = len(Nets_Arc_req_BHZ[i])
		for j in range(0, len_req_Arc_BHZ):
			Nets_Arc_req_BHZ[i][j] = Nets_Arc_req_BHZ[i][j].split('.')
	
	for j in range(0, len_events):
		for i in range(0, len(Nets_Arc_req_BHE[j])):
			if Nets_Arc_req_BHE[j][i] == ['BW', 'WETR', '', 'BHE']:
				del Nets_Arc_req_BHE[j][i]
				break
		
		for i in range(0, len(Nets_Arc_req_BHN[j])):
			if Nets_Arc_req_BHN[j][i] == ['BW', 'WETR', '', 'BHN']:
				del Nets_Arc_req_BHN[j][i]
				break
		
		for i in range(0, len(Nets_Arc_req_BHZ[j])):
			if Nets_Arc_req_BHZ[j][i] == ['BW', 'WETR', '', 'BHZ']:
				del Nets_Arc_req_BHZ[j][i]
				break
	
	
	for i in range(0, len_events):
		print "--------------------"
		print 'ARC-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHE)
		print 'ARC-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHN)
		print 'ARC-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHZ)
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/STATION/' + 'Report_station', 'a')
		eventsID = events[i]['event_id']
		Report.writelines(eventsID + '\n')		
		Report.writelines('---------------ArcLink---------------' + '\n')
		rep1 = 'ARC-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHE) + '\n'
		rep2 = 'ARC-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHN) + '\n'
		rep3 = 'ARC-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHZ) + '\n'
		Report.writelines(rep1)
		Report.writelines(rep2)
		Report.writelines(rep3)
		Report.writelines('----------------------------------' + '\n')
		Report.close()
		
	for i in range(0, len_events):
		Station_file1 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'All_ARC_Stations_BHE', 'w')
		pickle.dump(Nets_Arc_req_BHE[i], Station_file1)
		Station_file1.close()
		
		Station_file2 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'All_ARC_Stations_BHN', 'w')
		pickle.dump(Nets_Arc_req_BHN[i], Station_file2)
		Station_file2.close()
		
		Station_file3 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/STATION/' + 'All_ARC_Stations_BHZ', 'w')
		pickle.dump(Nets_Arc_req_BHZ[i], Station_file3)
		Station_file3.close()
		
	t_arc_2 = datetime.now()
	t_arc_21 = t_arc_2 - t_arc_1
	
	print "--------------------"
	print 'ARC-Time: (Availability)'
	print t_arc_21
	
	return Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t
