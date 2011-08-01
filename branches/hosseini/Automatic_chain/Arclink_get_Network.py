"""
?????????? ['BW', 'WETR', '', 'BHE']
Arclink: Gets the information about the available stations in a specific period of time (Events)
"""

from obspy.arclink import Client as Client_arclink
from obspy.core import UTCDateTime
from datetime import datetime
import pickle
import time
import os

# client_arclink = Client_arclink(timeout = 30, command_delay=0.1)
client_arclink = Client_arclink()

def Arclink_get_Network(len_events, events, Address_events):
	
	t_arc_1 = datetime.now()

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
	
	import ipdb; ipdb.set_trace()
	
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
     
                
"""
events = pickle.load(Event_file)

for i in range(0, len_events):
		#import os
		#folder = os.path.join(Address, 'Data', Period, events[i]['event_id'])
		#os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'])
		# for resp file
		os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'] + '/Arc_BH' + '/RESP')
		#os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'] + '/Arc_BH')

print 'Folders are Created!'
"""
