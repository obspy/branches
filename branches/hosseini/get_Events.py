"""
Getting list of events from NERIES
Selecting required events based on the desired parameters....
"""

from obspy.neries import Client as Client_neries
from datetime import datetime
import time
import pickle
import os

client_neries = Client_neries()

def get_Events(Address, min_datetime, max_datetime, min_magnitude, max_magnitude, \
		min_latitude, max_latitude, min_longitude, max_longitude, min_depth, max_depth, max_results):
	
	t_event_1 = datetime.now()
	
	events = client_neries.getEvents(min_datetime=min_datetime, max_datetime=max_datetime, \
		min_magnitude=min_magnitude, max_magnitude=max_magnitude, \
		min_latitude=min_latitude, max_latitude=max_latitude, \
		min_longitude=min_longitude, max_longitude=max_longitude, \
		min_depth = min_depth, max_depth=max_depth, max_results=max_results)
		
	# !!!!!!! You should change the str(t_event_1) 
	Period = min_datetime + '_' + max_datetime + '_' + str(min_magnitude) + '_' + str(t_event_1.hour) + '_' + str(t_event_1.minute) + '_' + str(t_event_1.second)
	     
	os.makedirs(Address + '/Data/' + Period)
	len_events = len(events)
	#import ipdb; ipdb.set_trace()
	print len_events
	Events_No = []
	
	for i in range(0, len_events):
		#if events[i]['magnitude'] >= 7:
		Events_No.append(i+1)
		print "Event No:" + " " + str(i+1)
		print "Date Time:" + " " + str(events[i]['datetime'])
		print "Depth:" + " " + str(events[i]['depth'])
		print "Event-ID:" + " " + events[i]['event_id']
		#print "Flynn-Region:" + " " + events[i]['flynn_region']
		print "Latitude:" + " " + str(events[i]['latitude'])
		print "Longitude:" + " " + str(events[i]['longitude'])
		print "Magnitude:" + " " + str(events[i]['magnitude'])
		print "-------------------------------------------------"
	
	Event_file = open(Address + '/Data/' + Period + '/list_event', 'w')
	pickle.dump(events, Event_file)
	Event_file.close()
	
	t_event_2 = datetime.now()
	t_event = t_event_2 - t_event_1
	
	print 'Events are saved!'
	print t_event
	
	return events, len_events, Period
