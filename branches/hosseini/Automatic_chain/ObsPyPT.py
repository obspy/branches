#CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import ipdb; ipdb.set_trace()

"""
ObsPyPT (ObsPy Plotting Tool)

Goal: Plotting tools for Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""


"""
- Import required Modules (Python and Obspy)
- Read INPUT file (Parameters)
- Parallel Requests

- plot all events
- plot IRIS stations
- plot ArcLink stations
- plot events
- Plotting
- Plot Ray Paths (event --> stations)
"""


# ------------------------Import required Modules (Python and Obspy)-------------
from mpl_toolkits.basemap import Basemap
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import commands
import pickle
import os

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def ObsPyPT():
	
	t1_pro = datetime.now()

	print '--------------------------------------------------------------------------------'
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'ObsPyPT ' + reset + '(' + bold + 'ObsPy P' + reset + 'lotting ' + bold + 'T' + reset + 'ool)' + reset + '\n'
	print '\t' + 'Plotting tools for Large Seismic Datasets' + '\n'
	print ':copyright:'
	print 'The ObsPy Development Team (devs@obspy.org)' + '\n'
	print ':license:'
	print 'GNU Lesser General Public License, Version 3'
	print '(http://www.gnu.org/copyleft/lesser.html)'
	print '--------------------------------------------------------------------------------'
	
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()
	
	# ------------------------Parallel Requests--------------------
	if input['nodes'] == 'Y':
		nodes(input)
	
	# ------------------------plot all events--------------------------------
	
	if input['plot_all_Events'] == 'Y':
		
		print '*********************'
		print 'Plot all Events'
		print '*********************'
		
		plot_all_events(input)
	
	# ------------------------plot IRIS stations--------------------------------
	if input['plot_IRIS'] == 'Y':
		
		print '*********************'
		print 'IRIS -- Plotting'
		print '*********************'
		
		plot_IRIS(input)
	
	# ------------------------plot ArcLink stations--------------------------------
	if input['plot_ARC'] == 'Y':
		
		print '*********************'
		print 'ArcLink -- Plotting'
		print '*********************'
		
		plot_ARC(input)
	
	# ------------------------plot events--------------------------------
	if input['plt_event'] == 'on':		
		plot_events(input)
	
	# ------------------------plot ray path--------------------------------
	
	
	
		
	# ---------------------------------------------------------------
	t2_pro = datetime.now()
	t_pro = t2_pro - t1_pro

	print '--------------------------------------------------------------------------------'
	print 'Thanks for using:' + '\n' 
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'ObsPyPT ' + reset + '(' + bold + 'ObsPy P' + reset + 'lotting ' + bold + 'T' + reset + 'ool)' + reset + '\n'

	print "Total Time:"
	print t_pro
	print '--------------------------------------------------------------------------------'



######################################################################################################################################
###################################################### Modules are defined here ######################################################
######################################################################################################################################


###################################################### read_input ######################################################

def read_input():	
	
	"""
	Read inputs from INPUT file
	This module will read the INPUT files which is located in the same folder as ObsPyDMT.py
	"""
	
	add = os.getcwd()
	add += '/INPUT'
	f = open(add)
	S = f.readlines()
	input = {}
	input['Address'] = S[3].split()[2]
	input['min_date'] = S[7].split()[2]
	input['max_date'] = S[8].split()[2]
	input['min_mag'] = float(S[9].split()[2])
	input['max_mag'] = float(S[10].split()[2])
	input['min_lat'] = float(S[12].split()[2])
	input['max_lat'] = float(S[13].split()[2])
	input['min_lon'] = float(S[14].split()[2])
	input['max_lon'] = float(S[15].split()[2])
	input['min_depth'] = float(S[17].split()[2])
	input['max_depth'] = float(S[18].split()[2])
	input['max_result'] = int(S[19].split()[2])
	input['t_before'] = float(S[21].split()[2])
	input['t_after'] = float(S[22].split()[2])

	input['get_events'] = S[26].split()[2]
	input['IRIS'] = S[27].split()[2]
	input['ArcLink'] = S[28].split()[2]
	
	input['mass'] = S[32].split()[2]	
	input['nodes'] = S[33].split()[2]

	input['waveform'] = S[37].split()[2]
	input['response'] = S[38].split()[2]
	
	input['net'] = S[42].split()[2]
	input['sta'] = S[43].split()[2]
	
	if S[44].split()[2] == "''":
		input['loc'] = ''
	elif S[44].split()[2] == '""':
		input['loc'] = ''
	else:
		input['loc'] = S[44].split()[2]
	
	input['cha'] = S[45].split()[2]
	input['BHE'] = S[46].split()[2]
	input['BHN'] = S[47].split()[2]
	input['BHZ'] = S[48].split()[2]	
	input['other'] = S[49].split()[2]
	
	input['lat_cba'] = S[55].split()[2]
	input['lon_cba'] = S[56].split()[2]
	input['mr_cba'] = S[57].split()[2]
	input['Mr_cba'] = S[58].split()[2]
	
	if S[59].split()[2] == 'None':
		input['mlat_rbb'] = None
	else:
		input['mlat_rbb'] = S[59].split()[2]
	
	if S[60].split()[2] == 'None':
		input['Mlat_rbb'] = None
	else:
		input['Mlat_rbb'] = S[60].split()[2]
	
	if S[61].split()[2] == 'None':
		input['mlon_rbb'] = None
	else:
		input['mlon_rbb'] = S[61].split()[2]
	
	if S[62].split()[2] == 'None':
		input['Mlon_rbb'] = None
	else:
		input['Mlon_rbb'] = S[62].split()[2]

	
	input['TEST'] = S[66].split()[2]
	input['TEST_no'] = int(S[67].split()[2])
	
	input['update_iris'] = S[71].split()[2]
	input['update_arc'] = S[72].split()[2]
	input['No_updating_IRIS'] = int(S[73].split()[2])
	input['No_updating_ARC'] = int(S[74].split()[2])

	input['QC_IRIS'] = S[78].split()[2]
	input['QC_ARC'] = S[79].split()[2]

	input['plt_event'] = S[83].split()[2]
	input['plot_IRIS'] = S[84].split()[2]
	input['plot_ARC'] = S[85].split()[2]
	input['plot_all_Events'] = S[86].split()[2]

	input['llcrnrlon'] = float(S[88].split()[2])
	input['llcrnrlat'] = float(S[89].split()[2])
	input['urcrnrlon'] = float(S[90].split()[2])
	input['urcrnrlat'] = float(S[91].split()[2])
	
	return input

###################################################### nodes ######################################################

def nodes(input):
	
	"""
	Downloading in Parallel way
	Please change the 'INPUT-Periods' file for different requests
	Suggestion: Do not request more than 10 in parallel...
	"""
	
	add = os.getcwd()
	add += '/INPUT-Periods'
	f = open(add)
	per_tty = f.readlines()
	
	for i in range(0, len(per_tty)):
		per_tty[i] = per_tty[i].split('_')
	
	if os.path.exists(input['Address'] + '/Data/' + 'tty-info') != True:
	
		if os.path.exists(input['Address'] + '/Data') != True:
			os.makedirs(input['Address'] + '/Data')
	
		tty = open(input['Address'] + '/Data/' + 'tty-info', 'w')
		
		tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[0][0] + \
				'_' + per_tty[0][1] + '_' + per_tty[0][2] + '_' + per_tty[0][3][:-1] + '  ,  ' +  '\n')
		
		tty.close()
		
	else:
		n = int(raw_input('Please enter a node number:' + '\n' + '(If you enter "-1", it means that the node number already exists in the file.)' + '\n'))
		print '-------------------------------------------------------------'
		
		if n == -1:
			print 'You entered "-1" -- the node number exists in the tty-info!'
			print '-------------------------------------------------------------'
		else: 
			tty = open(input['Address'] + '/Data/' + 'tty-info', 'a')
			tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
					'_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + per_tty[n][3][:-1] + '  ,  ' +  '\n')

			tty.close()		
	
	
	Address_data = input['Address'] + '/Data'
	
	tty = open(input['Address'] + '/Data/' + 'tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				
				input['min_date'] = tty_str[i][2].split('_')[0]
				input['max_date'] = tty_str[i][2].split('_')[1]
					
	return input

###################################################### plot_all_events ######################################################

def plot_all_events(input):	
	
	"""
	Plot all requested events
	"""
	
	Address_data = input['Address'] + '/Data'
	
	ls_period = os.listdir(Address_data)
	
	pre_ls_event = []
	for i in range(0, len(ls_period)):
		pre_ls_event.append(Address_data + '/' + ls_period[i])	
	
	for i in range(0, len(pre_ls_event)):
		print 'Plotting: ' + '\n' + str(pre_ls_event[i])
	print '*********************'
	
	ls_event_file = []
	for i in range(0, len(pre_ls_event)):
		if ls_period[i] != 'tty-info':
			ls_event_file.append(os.listdir(Address_data + '/' + ls_period[i]))
	
	ls_event = []
	
	for i in range(0, len(ls_event_file)):
		for j in range(0, len(ls_event_file[i])):
			if ls_event_file[i][j] != 'list_event':
				if ls_event_file[i][j] != 'EVENT':
					ls_event.append(pre_ls_event[0] + '/' + ls_event_file[i][j])
					print ls_event_file[i][j]
	
	add_IRIS_events = []
	for i in range(0, len(pre_ls_event)):
		if ls_period[i] != 'tty-info':
			add_IRIS_events.append(Address_data + '/' + ls_period[i] + '/list_event')
		
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
	
	#m.drawcoastlines()
	#m.drawmapboundary() 
	#m.fillcontinents(color='coral',lake_color='aqua')
	#m.fillcontinents()
	
	# draw parallels and meridians.
	m.drawparallels(np.arange(-90.,120.,30.))
	m.drawmeridians(np.arange(0.,420.,60.))
	
	m.drawlsmask()
	
	#plt.title("Mollweide Projection, Events");
	plt.title("All Events");
	
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
	import ipdb; ipdb.set_trace()
	for i in range(0, len(depth_event)):
		plt.text(x[i], y[i], ' ' + str(depth_event[i]), va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(Address_data + '/Plot_all_events' + '.pdf')
	
###################################################### plot_IRIS ######################################################

def plot_IRIS(input):	
	
	"""
	Plot all available IRIS stations
	"""
	
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

###################################################### plot_ARC ######################################################

def plot_ARC(input):	
	
	"""
	Plot all available ARC stations
	"""
	
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
	
	add_ARC_events = []
	for i in pre_ls_event:
		add_ARC_events.append(i + '/list_event')
		
	events_all = []
	
	for i in add_ARC_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	
	events_all_file = []
	
	for l in range(0, len(events_all)):
		events = pickle.load(events_all[l])
		for j in events:
			events_all_file.append(j)
	
	for l in range(0, len(ls_event)):
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/Input_Syn_BHE', 'r')
		ARC_BHE = ls_stas_open.readlines()	
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/Input_Syn_BHN', 'r')
		ARC_BHN = ls_stas_open.readlines()
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/STATION/Input_Syn_BHZ', 'r')
		ARC_BHZ = ls_stas_open.readlines()
		ls_stas_open.close()
		
		for i in events_all_file:
		
			lon_event = []
			lat_event = []			
			
			if i['event_id'] == ls_event[l].split('/')[-1]:
				lat_event.append(i['latitude'])
				lon_event.append(i['longitude'])
				Address = ls_event[l]
			
			
			if input['BHE'] == 'Y':
				lat_ARC_BHE = []
				lon_ARC_BHE = []
							
				for j in range(0, len(ARC_BHE)):
					lat_ARC_BHE.append(float(ARC_BHE[j].split(',')[4]))
					lon_ARC_BHE.append(float(ARC_BHE[j].split(',')[5]))
							
			if input['BHN'] == 'Y':
				lat_ARC_BHN = []
				lon_ARC_BHN = []
							
				for j in range(0, len(ARC_BHN)):
					lat_ARC_BHN.append(float(ARC_BHN[j].split(',')[4]))
					lon_ARC_BHN.append(float(ARC_BHN[j].split(',')[5]))
				
			if input['BHZ'] == 'Y':
				lat_ARC_BHZ = []
				lon_ARC_BHZ = []
							
				for j in range(0, len(ARC_BHZ)):
					lat_ARC_BHZ.append(float(ARC_BHZ[j].split(',')[4]))
					lon_ARC_BHZ.append(float(ARC_BHZ[j].split(',')[5]))
			
			import ipdb; ipdb.set_trace()
			
			if input['BHE'] == 'Y':			
				
				fig = open(ls_event[l] + '/ARC/STATION/FIGS', 'w')
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
				plt.title("ARC-Stations-BHE");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_ARC_BHE, lat_ARC_BHE)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/ARC/STATION/FIGS' + '/ARC_BHE' + '.pdf')
			
			
			if input['BHN'] == 'Y':			
				
				fig = open(ls_event[l] + '/ARC/STATION/FIGS', 'w')
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
				plt.title("ARC-Stations-BHN");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_ARC_BHN, lat_ARC_BHN)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/ARC/STATION/FIGS' + '/ARC_BHN' + '.pdf')
			
			
			if input['BHZ'] == 'Y':			
				
				fig = open(ls_event[l] + '/ARC/STATION/FIGS', 'w')
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
				plt.title("ARC-Stations-BHZ");
				
				x, y = m(lon_event, lat_event)
				m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
				
				x, y = m(lon_ARC_BHZ, lat_ARC_BHZ)
				m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
				plt.savefig(ls_event[l] + '/ARC/STATION/FIGS' + '/ARC_BHZ' + '.pdf')

###################################################### plot_events ######################################################

def plot_events(input):
	
	"""
	Plot a map that shows all requested events...
	ATTENTION: llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat --> have been imported for local plotting
	"""
	
	Address_data = input['Address'] + '/Data'
	
	pre_ls_event = []
	
	tty = open(input['Address'] + '/Data/' + 'tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				pre_ls_event.append(Address_data + '/' + tty_str[i][2])
	
	for i in range(0, len(pre_ls_event)):
		print 'Updating for: ' + '\n' + str(pre_ls_event[i])
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
	
	
	lon_event = []
	lat_event = []			
	name_event = []
	
	for i in events_all_file:
		lat_event.append(i['latitude'])
		lon_event.append(i['longitude'])
		name_event.append(i['depth'])
		
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
	plt.title("Events");
	
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len(lat_event)):
		plt.text(x[i], y[i], ' ' + name_event[i], va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(pre_ls_event[0] + '/EVENT' + '/Plot_events' + '.pdf')

###################################################### ray_path ######################################################

def ray_path(Address, Period, file_name, events, Ser_name, lon_event, lat_event, name_event, Num_Event, \
		lons_sta, lats_sta, names_sta):
	
	"""
	Plot the ray path for each event to all available stations
	"""
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	#m = Basemap(projection='moll', lon_0=-100, lat_0=39, resolution='c')
	m = Basemap(projection='moll', lon_0=lon_event, lat_0=lat_event, resolution='c')
	
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
	
	#plt.title("Mollweide Projection, Ray path");    # ipdb.set_trace()
	    # ipdb.set_trace()
		
	if Ser_name == '/IRIS/':
		plt.title("IRIS");
		lons_sta_float = []
		lats_sta_float = []
		for X in lons_sta:
			lons_sta_float.append(float(X))
		for X in lats_sta:
			lats_sta_float.append(float(X))
		x, y = m(lons_sta_float, lats_sta_float)
		color = 'blue'
		color1 = 'red'
	elif Ser_name == '/ARC/':
		plt.title("Arclink");
		x, y = m(lons_sta, lats_sta)
		color = 'blue'
		color1 = 'cyan'
	
	m.scatter(x, y, 20, color=color1, marker="v", edgecolor="k", zorder=10)

	for i in range(0, len(names_sta)):
		#plt.text(x[i], y[i], ' ' + names_sta[i], va="top", family="monospace", weight="bold")
		plt.text(x[i], y[i], ' ', va="top", size = 'x-small', family="monospace", weight="bold")
		
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 20, color="black", marker="o", edgecolor="k", zorder=3)
	
	# Return the great circles drawn from one event to all stations
	if Ser_name == '/IRIS/':
		for i in range(0, len(lats_sta)):
			m.drawgreatcircle(lon_event, lat_event, lons_sta_float[i], lats_sta_float[i], \
			color = color, zorder=2, linestyle='-')
		plt.text(x, y, ' ' + name_event, va="top", family="monospace", color = 'black', size = 'x-small', weight="bold")
		plt.savefig(Address + '/Data/' + Period + '/' + events[file_name]['event_id'] + '/IRIS/' + str(file_name) + '.pdf')
	
	elif Ser_name == '/ARC/':
		for i in range(0, len(lats_sta)):
			m.drawgreatcircle(lon_event, lat_event, lons_sta[i], lats_sta[i], \
			color = color, linestyle='-')
		plt.text(x, y, ' ' + name_event, va="top", size = 'x-small', family="monospace", weight="bold")
		plt.savefig(Address + '/Data/' + Period + '/' + events[file_name]['event_id'] + '/Arc_BH/' + str(file_name) + '.pdf')


if __name__ == "__main__":
	status = ObsPyPT()
	sys.exit(status)

'''
# ------------------------Plotting the Ray Paths-----------------------------
from ray_path import *
temp1 = 0
for i in range(0, len_events):
		lons_sta_new_IRIS = [] 
		lats_sta_new_IRIS = [] 
		names_sta_new_IRIS = []
		for j in range(0, Len_Lat_Lon_IRIS[i]):
			lons_sta_new_IRIS.append(lons_sta_IRIS[j + temp1]) 
			lats_sta_new_IRIS.append(lats_sta_IRIS[j+ temp1]) 
			names_sta_new_IRIS.append(names_sta_IRIS[j + temp1])
		temp1 = Len_Lat_Lon_IRIS[i]
			
		ray_path(Address, Period, file_name = i, events = events, Ser_name = '/IRIS/', \
		lon_event = lon_event[i], lat_event = lat_event[i], \
		name_event = name_event[i], Num_Event = len_events, lons_sta = \
			lons_sta_new_IRIS, lats_sta = lats_sta_new_IRIS, names_sta = names_sta_new_IRIS)


temp1 = 0
for i in range(0, len_events):
		lons_sta_new_ARC = [] 
		lats_sta_new_ARC = [] 
		names_sta_new_ARC = []
		for j in range(0, Len_Lat_Lon_ARC[i]):
			lons_sta_new_ARC.append(lons_sta_ARC[j + temp1]) 
			lats_sta_new_ARC.append(lats_sta_ARC[j+ temp1]) 
			names_sta_new_ARC.append(names_sta_ARC[j + temp1])
		temp1 = Len_Lat_Lon_ARC[i]
			
		ray_path(Address, Period, file_name = i, events = events, Ser_name = '/ARC/', \
		lon_event = lon_event[i], lat_event = lat_event[i], \
		name_event = name_event[i], Num_Event = len_events, lons_sta = \
			lons_sta_new_ARC, lats_sta = lats_sta_new_ARC, names_sta = names_sta_new_ARC)

#plt.savefig(Address + '/Data/figure.pdf')
plt.show()

t2_pro = datetime.now()
t_pro = t2_pro - t1_pro

print "Total Time:"
print t_pro



"""
from all_to_ascii import *

for i in range(0, len_events):
	event = events[i]
	all_to_ascii(Period, event, Address)
"""

'''
# ------------------------Trash-----------------------------
'''
lons_lats_names_sta = load_stations(Lon = Lon_IRIS, Lat = Lat_IRIS, name = name_IRIS, \
	Len_Lat_Lon = Len_Lat_Lon_IRIS, Num_Event = len_events, Address = Address, Period = Period)
lons_sta = []
lats_sta = []
names_sta = []

lons_sta.append(lons_lats_names_sta[0])
lats_sta.append(lons_lats_names_sta[1])
names_sta.append(lons_lats_names_sta[2])
'''
