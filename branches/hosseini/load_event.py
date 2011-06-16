"""
Load events from the directory
get the Lat, Lon and name (depth) of each
"""

import pickle

def load_event(Num_Event, Address_events):	
	
	Event_file = open(Address_events + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	lat_event = []
	lon_event = []
	name_event = []
	
	for i in range(0, Num_Event):
		lat_event.append(events[i]['latitude'])
		lon_event.append(events[i]['longitude'])
		name_event.append(str(events[i]['depth']))
		
	return lat_event, lon_event, name_event
		
