"""
Getting list of events from NERIES (a client for the Seismic Data Portal (http://www.seismicportal.eu))
"""

from obspy.neries import Client as Client_neries
from datetime import datetime
import time
import pickle
import os

client_neries = Client_neries()

def get_Events(input):
	
	t_event_1 = datetime.now()
	
	events = client_neries.getEvents(min_datetime=input['min_date'], max_datetime=input['max_date'], \
		min_magnitude=input['min_mag'], max_magnitude=input['max_mag'], \
		min_latitude=input['min_lat'], max_latitude=input['max_lat'], \
		min_longitude=input['min_lon'], max_longitude=input['max_lon'], \
		min_depth = input['min_depth'], max_depth=input['max_depth'], max_results=input['max_result'])
		
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		#+ '_' + \
		#str(t_event_1.month) + '_'+ str(t_event_1.day) + '_' + str(t_event_1.hour) + '_' + \
		#str(t_event_1.minute) + '_' + str(t_event_1.second)
	
	Address_events = input['Address'] + '/Data/' + Period
	
	os.makedirs(Address_events)
	len_events = len(events)
	
	print 'Length of the events found based on the inputs:'
	print len_events
	
	Events_No = []
	#import ipdb; ipdb.set_trace()
	for i in range(0, len_events):
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
	
	Event_file = open(Address_events + '/list_event', 'w')
	pickle.dump(events, Event_file)
	Event_file.close()
		
	print 'Events are saved!'
	
	print 'Length of events:'
	print len_events
	
	t_event_2 = datetime.now()
	t_event = t_event_2 - t_event_1
	
	print 'Time for getting and saving the events:'
	print t_event
	
	return events, len_events, Period, Address_events
