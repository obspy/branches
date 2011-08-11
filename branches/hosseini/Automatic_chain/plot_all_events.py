"""
Plot all requested events
"""

from obspy.core import read
import numpy as np
import os
import glob
import pickle
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def plot_all_events(input):	
		
	Address_data = input['Address'] + '/Data'
	
	ls_period = os.listdir(Address_data)
	
	pre_ls_event = []
	for i in range(0, len(ls_period)):
		pre_ls_event.append(Address_data + '/' + ls_period[i])	
	
	for i in range(0, len(pre_ls_event)):
		print 'Plotting: ' + '\n' + str(pre_ls_event[i])
	print '*********************'
	
	ls_event_file = []
	for i in pre_ls_event:
		ls_event_file.append(os.listdir(i))
	
	ls_event = []
	
	for i in range(0, len(ls_event_file)):
		for j in range(0, len(ls_event_file[i])):
			if ls_event_file[i][j] != 'list_event':
				if ls_event_file[i][j] != 'EVENT':
					ls_event.append(pre_ls_event[0] + '/' + ls_event_file[i][j])
					print ls_event_file[i][j]
	
	add_IRIS_events = []
	for i in pre_ls_event:
		add_IRIS_events.append(i + '/list_event')
		
	events_all = []
	
	for i in add_IRIS_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	
	events_all_file = []
	
	for l in range(0, len(events_all)):
		events = pickle.load(events_all[l])
		for j in events:
			events_all_file.append(j)
	
	dic_event = {}
	
	for i in range(0, len(events_all_file)):
		
		event_lat = events_all_file[i]['latitude']
		event_lon = events_all_file[i]['longitude']
		event_depth = events_all_file[i]['depth']
		event_id = events_all_file[i]['event_id']
		
		dic_event[i] ={'event_id': event_id, 'event_lat': event_lat, \
						'event_lon': event_lon, 'event_depth': event_depth}
	
	lon_event = []
	lat_event = []
	depth_event = []
		
	for i in range(0, len(dic_event)):
		lon_event.append(dic_event[i]['event_lon'])
		lat_event.append(dic_event[i]['event_lat'])
		depth_event.append(dic_event[i]['event_depth'])
	
	
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	# lat_0=lat_event[0], determines that center of the map has been aligend to the first event
	
	m = Basemap(projection='moll', lon_0=lon_event[0], lat_0=lat_event[0], resolution='c')
	#m = Basemap(projection='moll', lon_0=180, lat_0=0, resolution='c')
	
	# Different Options for drawing the Earth:
	#m = Basemap(projection='lcc',lon_0=0,resolution='c')
	#m.bluemarble()
	#m.drawcountries(linewidth=2)
	
	m.drawcoastlines()
	#m.fillcontinents(color='coral',lake_color='aqua')
	m.fillcontinents()
	# draw parallels and meridians.
	m.drawparallels(np.arange(-90.,120.,30.))
	m.drawmeridians(np.arange(0.,420.,60.))
	m.drawmapboundary() 
	
	#plt.title("Mollweide Projection, Events");
	plt.title("All Events");
	
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len(depth_event)):
		plt.text(x[i], y[i], ' ' + depth_event[i], va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(Address_data + '/Plot_all_events' + '.pdf')
	
