"""
Plot all available IRIS stations
"""

from obspy.core import read
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pickle
from nodes_update import *


def plot_IRIS(input):	
		
	Address_data = input['Address'] + '/Data'
	
	ls_period = os.listdir(Address_data)
	
	pre_ls_event = []
	for i in range(0, len(ls_period)):
		pre_ls_event.append(Address_data + '/' + ls_period[i])	

	pre_ls_event = nodes_update(input, pre_ls_event)
	
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
	
	for l in range(0, len(ls_event)):
		
		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/Input_Syn_BHE', 'r')
		IRIS_BHE = ls_stas_open.readlines()	
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/Input_Syn_BHN', 'r')
		IRIS_BHN = ls_stas_open.readlines()
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/STATION/Input_Syn_BHZ', 'r')
		IRIS_BHZ = ls_stas_open.readlines()
		ls_stas_open.close()
		
		for i in events_all_file:
		
			lon_event = []
			lat_event = []			
			
			if i['event_id'] == ls_event[l].split('/')[-1]:
				lat_event.append(i['latitude'])
				lon_event.append(i['longitude'])
				Address = ls_event[l]
			
			
			if input['BHE'] == 'Y':
				lat_IRIS_BHE = []
				lon_IRIS_BHE = []
							
				for j in range(0, len(IRIS_BHE)):
					lat_IRIS_BHE.append(float(IRIS_BHE[j].split(',')[4]))
					lon_IRIS_BHE.append(float(IRIS_BHE[j].split(',')[5]))
							
			if input['BHN'] == 'Y':
				lat_IRIS_BHN = []
				lon_IRIS_BHN = []
							
				for j in range(0, len(IRIS_BHN)):
					lat_IRIS_BHN.append(float(IRIS_BHN[j].split(',')[4]))
					lon_IRIS_BHN.append(float(IRIS_BHN[j].split(',')[5]))
				
			if input['BHZ'] == 'Y':
				lat_IRIS_BHZ = []
				lon_IRIS_BHZ = []
							
				for j in range(0, len(IRIS_BHZ)):
					lat_IRIS_BHZ.append(float(IRIS_BHZ[j].split(',')[4]))
					lon_IRIS_BHZ.append(float(IRIS_BHZ[j].split(',')[5]))
			
			import ipdb; ipdb.set_trace()
			
			if input['BHE'] == 'Y':			
				
				fig = open(ls_event[l] + '/IRIS/STATION/FIGS', 'w')
				fig.close()
				
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
				plt.title("IRIS-Stations-BHE");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_IRIS_BHE, lat_IRIS_BHE)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/IRIS/STATION/FIGS' + '/IRIS_BHE' + '.pdf')
			
			
			if input['BHN'] == 'Y':			
				
				fig = open(ls_event[l] + '/IRIS/STATION/FIGS', 'w')
				fig.close()
				
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
				plt.title("IRIS-Stations-BHN");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_IRIS_BHN, lat_IRIS_BHN)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/IRIS/STATION/FIGS' + '/IRIS_BHN' + '.pdf')
			
			
			if input['BHZ'] == 'Y':			
				
				fig = open(ls_event[l] + '/IRIS/STATION/FIGS', 'w')
				fig.close()
				
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
				plt.title("IRIS-Stations-BHZ");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_IRIS_BHZ, lat_IRIS_BHZ)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/IRIS/STATION/FIGS' + '/IRIS_BHZ' + '.pdf')
			
			
			
		
		
		
		
		
