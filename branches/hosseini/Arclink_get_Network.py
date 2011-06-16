"""
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

def Arclink_get_Network(len_events, events, Address, Period):
	
	t_arc_1 = datetime.now()

	t = []
	Networks_Arclink = []
	Nets_Arc_req_BHE = []
	Nets_Arc_req_BHN = []
	Nets_Arc_req_BHZ = []

	for i in range(0, len_events):
		t.append(UTCDateTime(events[i]['datetime']))

		while True:
			try:
				Networks_Arclink.append(client_arclink.getNetworks(t[i]-10, t[i]+10))
				break
			except Exception, e:
				print e
				
		nets_Arc_req_BHE=sorted([X for X in Networks_Arclink[i].keys() if ".BHE" in X])
		Nets_Arc_req_BHE.append(nets_Arc_req_BHE)	
		nets_Arc_req_BHN=sorted([X for X in Networks_Arclink[i].keys() if ".BHN" in X])
		Nets_Arc_req_BHN.append(nets_Arc_req_BHN)
		nets_Arc_req_BHZ=sorted([X for X in Networks_Arclink[i].keys() if ".BHZ" in X])
		Nets_Arc_req_BHZ.append(nets_Arc_req_BHZ)

	for i in range(0, len_events):
		#import os
		#folder = os.path.join(Address, 'Data', Period, events[i]['event_id'])
		#os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'])
		# for resp file
		os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'] + '/Arc_BH' + '/RESP')
		#os.makedirs(Address + '/Data/' + Period + '/' + events[i]['event_id'] + '/Arc_BH')

	print 'Folders are Created!'

	t_arc_2 = datetime.now()
	t_arc_21 = t_arc_2 - t_arc_1
	
	print 'Time:'
	print t_arc_21
	
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
	
	print 'length of events:'
	print len_events
	print 'length of required Arclink channels:'
	print len_req_Arc_BHE
	
	return Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t          
                
"""
events = pickle.load(Event_file)
"""
