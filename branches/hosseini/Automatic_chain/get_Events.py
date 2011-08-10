"""
Getting list of events from NERIES (a client for the Seismic Data Portal (http://www.seismicportal.eu))
"""

from obspy.neries import Client as Client_neries
from datetime import datetime
import time
import pickle
import os
import shutil
import sys

client_neries = Client_neries()

def get_Events(input):
	
	t_event_1 = datetime.now()
	
	events = client_neries.getEvents(min_datetime=input['min_date'], max_datetime=input['max_date'], \
		min_magnitude=input['min_mag'], max_magnitude=input['max_mag'], \
		min_latitude=input['min_lat'], max_latitude=input['max_lat'], \
		min_longitude=input['min_lon'], max_longitude=input['max_lon'], \
		min_depth = input['min_depth'], max_depth=input['max_depth'], max_results=input['max_result'])
		
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	
	Address_events = input['Address'] + '/Data/' + Period
	
	if os.path.exists(Address_events) == True:
		print '-------------------------------------------------------------'
		
		if raw_input('Folder for requested Period (min/max) and Magnitude (min/max) exists in your directory.' + '\n\n' + \
			'You could either close the program and try updating your folder OR remove the tree, continue the program and download again.' + \
			'\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
			print '-------------------------------------------------------------'
			shutil.rmtree(Address_events)
			os.makedirs(Address_events)
		
		else:
			print '-------------------------------------------------------------'
			print 'So...you decided to update your folder...Ciao'
			print '-------------------------------------------------------------'
			sys.exit()
			
	else:
		os.makedirs(Address_events)
	
	
	os.makedirs(Address_events + '/EVENT')
	
	len_events = len(events)
	
	print 'Length of the events found based on the inputs:'
	print len_events
	
	Events_No = []

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
				
	
	Event_cat = open(Address_events + '/EVENT/' + 'EVENT-CATALOG', 'w')
	Event_cat.writelines(str(Period) + '\n')
	Event_cat.writelines('------------------------------------------------------' + '\n')
	Event_cat.writelines('Information about the requested Events:' + '\n\n')
	#Event_cat.writelines('Number of Events: ' + str(i+1) + '\n')
	Event_cat.writelines('min datetime: ' + str(input['min_date']) + '\n')
	Event_cat.writelines('max datetime: ' + str(input['max_date']) + '\n')
	Event_cat.writelines('min magnitude: ' + str(input['min_mag']) + '\n')
	Event_cat.writelines('max magnitude: ' + str(input['max_mag']) + '\n')
	Event_cat.writelines('min latitude: ' + str(input['min_lat']) + '\n')
	Event_cat.writelines('max latitude: ' + str(input['max_lat']) + '\n')
	Event_cat.writelines('min longitude: ' + str(input['min_lon']) + '\n')
	Event_cat.writelines('max longitude: ' + str(input['max_lon']) + '\n')
	Event_cat.writelines('min depth: ' + str(input['min_depth']) + '\n')
	Event_cat.writelines('max depth: ' + str(input['max_depth']) + '\n')
	Event_cat.writelines('------------------------------------------------------' + '\n\n')
	Event_cat.close()
	
	
	
	for j in range(0, len_events):
		Event_cat = open(Address_events + '/EVENT/' + 'EVENT-CATALOG', 'a')
		Event_cat.writelines("Event No: " + str(j+1) + '\n')
		Event_cat.writelines("Event-ID: " + str(events[j]['event_id']) + '\n')
		Event_cat.writelines("Date Time: " + str(events[j]['datetime']) + '\n')
		Event_cat.writelines("Magnitude: " + str(events[j]['magnitude']) + '\n')
		Event_cat.writelines("Depth: " + str(events[j]['depth']) + '\n')
		Event_cat.writelines("Latitude: " + str(events[j]['latitude']) + '\n')
		Event_cat.writelines("Longitude: " + str(events[j]['longitude']) + '\n')
		
		try:
			Event_cat.writelines("Flynn-Region: " + str(events[j]['flynn_region']) + '\n')
		
		except Exception, e:
			Event_cat.writelines("Flynn-Region: " + 'None' + '\n')
		
		Event_cat.writelines('------------------------------------------------------' + '\n')
		Event_cat.close()
	
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
