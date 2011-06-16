"""
Load events from the directory
get the Lat, Lon and name of each
"""

import pickle

def load_event(Num_Event, Address, Period):	
	
	Event_file = open(Address + '/Data/' + Period + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	lat_event = []
	lon_event = []
	name_event = []
	
	for i in range(0, Num_Event):
		lat_event.append(events[i]['latitude'])
		lon_event.append(events[i]['longitude'])
		name_event.append(str(events[i]['depth']))
		
	return lat_event, lon_event, name_event
		
