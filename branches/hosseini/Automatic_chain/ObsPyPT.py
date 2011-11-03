#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------
#   Filename:  ObsPyPT.py
#   Author:    S. Kasra Hosseini zad
#   Email:     hosseini@geophysik.uni-muenchen.de
#
#   Copyright (C) 2011 Seyed Kasra Hosseini zad
#-------------------------------------------------------------------


"""
ObsPyPT (ObsPy Plotting Tool)

Goal: Plotting tools for Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""

#for debugging: import ipdb; ipdb.set_trace()

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
from obspy.core import read

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import commands
import glob
import shutil
import pickle
import os

try:
	from mpl_toolkits.basemap import Basemap
except Exception, error:
    print error
    print "Missing dependencies, no plotting available."


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
	
	add_ress = get_address(input, interactive = input['inter_address'])
	(net, sta, loc, cha) = get_info(input, interactive = input['inter_address'])
	add_save = address_save(input, interactive = input['inter_address'])
	
	plt_file = plot_file(add_ress, add_save, net, sta, loc, cha)
			
	# ------------------------plot events--------------------------------
	if input['plt_event'] == 'Y':
		
		print '*********************'
		print 'event -- Plotting'
		print '*********************'
					
		plot_event(input, add_ress, add_save)
				
	# ------------------------plot IRIS stations--------------------------------
	if input['plt_sta'] == 'Y':
			
		print '*********************'
		print 'Stations -- Plotting'
		print '*********************'
			
		plot_sta(input, add_ress, add_save)
		
	# ------------------------plot ray path--------------------------------
	if input['plt_ray'] == 'Y':
			
		print '*********************'
		print 'Plot ray path'
		print '*********************'
			
		plot_ray(input, add_ress, add_save)
			
	# ------------------------plot all events--------------------------------
	
	if input['plot_all_Events'] == 'Y':
		
		print '*********************'
		print 'Plot all Events'
		print '*********************'
		
		plot_all_events(input)
		
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
	input['inter_address'] = S[4].split()[2]
	input['min_date'] = S[8].split()[2]
	input['max_date'] = S[9].split()[2]
	input['min_mag'] = float(S[10].split()[2])
	input['max_mag'] = float(S[11].split()[2])
	input['min_lat'] = float(S[13].split()[2])
	input['max_lat'] = float(S[14].split()[2])
	input['min_lon'] = float(S[15].split()[2])
	input['max_lon'] = float(S[16].split()[2])
	input['min_depth'] = float(S[18].split()[2])
	input['max_depth'] = float(S[19].split()[2])
	input['max_result'] = int(S[20].split()[2])
	input['t_before'] = float(S[22].split()[2])
	input['t_after'] = float(S[23].split()[2])

	input['get_events'] = S[27].split()[2]
	input['IRIS'] = S[28].split()[2]
	input['ArcLink'] = S[29].split()[2]
	
	input['mass'] = S[33].split()[2]	
	input['nodes'] = S[34].split()[2]

	input['waveform'] = S[38].split()[2]
	input['response'] = S[39].split()[2]
	input['SAC'] = S[40].split()[2]
	
	input['net'] = S[44].split()[2]
	input['sta'] = S[45].split()[2]
	
	if S[46].split()[2] == "''":
		input['loc'] = ''
	elif S[46].split()[2] == '""':
		input['loc'] = ''
	else:
		input['loc'] = S[46].split()[2]
	
	input['cha'] = S[47].split()[2]
	input['BHE'] = S[48].split()[2]
	input['BHN'] = S[49].split()[2]
	input['BHZ'] = S[50].split()[2]	
	input['other'] = S[51].split()[2]
		
	if S[57].split()[2] == 'None':
		input['lat_cba'] = None
	else:
		input['lat_cba'] = S[57].split()[2]
		
	if S[58].split()[2] == 'None':
		input['lon_cba'] = None
	else:
		input['lon_cba'] = S[58].split()[2]
	
	if S[59].split()[2] == 'None':
		input['mr_cba'] = None
	else:
		input['mr_cba'] = S[59].split()[2]
	
	if S[60].split()[2] == 'None':
		input['Mr_cba'] = None
	else:
		input['Mr_cba'] = S[60].split()[2]
	
		
	if S[61].split()[2] == 'None':
		input['mlat_rbb'] = None
	else:
		input['mlat_rbb'] = S[61].split()[2]
	
	if S[62].split()[2] == 'None':
		input['Mlat_rbb'] = None
	else:
		input['Mlat_rbb'] = S[62].split()[2]
	
	if S[63].split()[2] == 'None':
		input['mlon_rbb'] = None
	else:
		input['mlon_rbb'] = S[63].split()[2]
	
	if S[64].split()[2] == 'None':
		input['Mlon_rbb'] = None
	else:
		input['Mlon_rbb'] = S[64].split()[2]

	
	input['TEST'] = S[68].split()[2]
	input['TEST_no'] = int(S[69].split()[2])
	
	input['update_iris'] = S[73].split()[2]
	input['update_arc'] = S[74].split()[2]
	input['No_updating_IRIS'] = int(S[75].split()[2])
	input['No_updating_ARC'] = int(S[76].split()[2])

	input['QC_IRIS'] = S[80].split()[2]
	input['QC_ARC'] = S[81].split()[2]
	
	input['email'] = S[85].split()[2]
	input['email_address'] = S[86].split()[2]
	
	input['report'] = S[90].split()[2]
	
	input['plt_event'] = S[94].split()[2]
	input['plt_sta'] = S[95].split()[2]
	input['plt_ray'] = S[96].split()[2]

	input['llcrnrlon'] = float(S[98].split()[2])
	input['llcrnrlat'] = float(S[99].split()[2])
	input['urcrnrlon'] = float(S[100].split()[2])
	input['urcrnrlat'] = float(S[101].split()[2])
	
	input['lat_0'] = float(S[103].split()[2])
	input['lon_0'] = float(S[104].split()[2])
	
	input['plt_folder'] = S[106].split()[2]
	input['plt_save'] = S[107].split()[2]
	
	return input

###################################################### get_address ######################################################

def get_address(input, interactive = 'Y'):
	
	"""
	This program gets the address of target stations for plotting
	"""
	
	if interactive == 'Y':
		print '----------------------------------------------------'
		address = raw_input('Please enter the target address:' + '\n')
		print '----------------------------------------------------'
		
	else:
		address = input['plt_folder']
	
	return address

###################################################### get_info ######################################################

def get_info(input, interactive = 'Y'):
	
	"""
	Get the required info for plotting...
	"""
	if interactive == 'Y':
		print 'To proceed to the next step, we need:'
		print '--------------------'
		net = raw_input('Network:' + '\n')
		print '--------------------'
		sta = raw_input('Station:' + '\n')
		print '--------------------'
		loc = raw_input('Location:' + '\n')
		print '--------------------'
		cha = raw_input('Channel:' + '\n')
		print '--------------------'

	else:
		net = input['net']
		sta = input['sta']
		loc = input['loc']
		cha = input['cha']
	
	return net, sta, loc, cha

###################################################### address_save ######################################################

def address_save(input, interactive = 'Y'):
	
	"""
	This program gets the address where it should save the figures
	"""
	
	if interactive == 'Y':
		print '----------------------------------------------------'
		address = raw_input('Please enter the address, where you want to save the figures:' + '\n')
		print '----------------------------------------------------'
	
	else:
		address = input['plt_save']
	
	return address

###################################################### plot_file ######################################################

def plot_file(add_ress, add_save, net, sta, loc, cha):
	
	"""
	Write a file that contains info about event and stations...
	"""
	
	if os.path.exists(add_save + '/plot_file') == True:
		print '--------------------'
		print '"plot_file" exists in: ' + add_ress
		print '--------------------'
		ques = raw_input('Do you want to update the file: (Y/N)' + '\n')
		
		if ques == 'Y':
			print '--------------------'
			print 'ObsPyPT is about to generate plot_file...'
			print '--------------------'
			
			os.remove(add_save + '/plot_file')
			
			gl_sta = glob.glob(add_ress + '/' + net + '.' + sta + '.' + loc + '.' + cha)
			file_plt = open(add_save + '/' + 'plot_file', 'w')
			file_plt.close()
			
			for i in gl_sta:
				file_plt = open(add_save + '/' + 'plot_file', 'a')
				st = read(i)
				str_file = st[0].stats['network'] + ',' + st[0].stats['station'] + ',' + \
							st[0].stats['location'] + ',' + st[0].stats['channel'] + ',' + str(st[0].stats['sac']['stla']) + \
							',' +  str(st[0].stats['sac']['stlo']) + ',' +  str(st[0].stats['sac']['stel']) + ',' + 'burrial' + ',' + 'event_id' + ',' + \
							 str(st[0].stats['sac']['evla']) + ',' + str(st[0].stats['sac']['evlo']) + ',' + str(st[0].stats['sac']['evdp']) + ',' + \
							str(st[0].stats['sac']['mag'])  + ',' + '\n'
				file_plt.writelines(str_file)
				file_plt.close()
							
	else:
		print '--------------------'
		print 'ObsPyPT is about to generate plot_file...'
		print '--------------------'
		
		gl_sta = glob.glob(add_ress + '/' + net + '.' + sta + '.' + loc + '.' + cha)
		file_plt = open(add_save + '/' + 'plot_file', 'w')
		file_plt.close()
		
		for i in gl_sta:
			file_plt = open(add_save + '/' + 'plot_file', 'a')
			st = read(i)
			str_file = st[0].stats['network'] + ',' + st[0].stats['station'] + ',' + \
						st[0].stats['location'] + ',' + st[0].stats['channel'] + ',' + str(st[0].stats['sac']['stla']) + \
						',' +  str(st[0].stats['sac']['stlo']) + ',' +  str(st[0].stats['sac']['stel']) + ',' + 'burrial' + ',' + 'event_id' + ',' + \
						 str(st[0].stats['sac']['evla']) + ',' + str(st[0].stats['sac']['evlo']) + ',' + str(st[0].stats['sac']['evdp']) + ',' + \
						str(st[0].stats['sac']['mag'])  + ',' + '\n'
			file_plt.writelines(str_file)
			file_plt.close()
		
###################################################### plot_events ######################################################

def plot_event(input, add_ress, add_save):
	
	"""
	Plot a map that shows the requested event...
	"""
	
	fi_plt = open(add_save + '/' + 'plot_file', 'r')
	file_plt = fi_plt.readlines()
	
	for i in range(0, len(file_plt)):
		file_plt[i] = file_plt[i].split(',')
	
	lat_ev = float(file_plt[0][9])
	lon_ev = float(file_plt[0][10])
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	m = Basemap(projection='moll', lon_0=lon_ev, lat_0=lat_ev, resolution='c')
	
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
	plt.title("Event");
	
	x, y = m(lon_ev, lat_ev)
	m.scatter(x, y, 40, color="black", marker="o", edgecolor="k", zorder=3)
	
	plt.text(x, y, ' ' + str(file_plt[0][11]), va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(add_save + '/plot_event' + '.pdf')	

###################################################### plot_sta ######################################################

def plot_sta(input, add_ress, add_save):	
	
	"""
	Plot all available IRIS stations
	"""
	
	fi_plt = open(add_save + '/' + 'plot_file', 'r')
	file_plt = fi_plt.readlines()
	
	for i in range(0, len(file_plt)):
		file_plt[i] = file_plt[i].split(',')
	
	lat_ev = float(file_plt[0][9])
	lon_ev = float(file_plt[0][10])
					
	plt.clf()
		
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
				
	m = Basemap(projection='moll', lon_0=lon_ev, lat_0=lat_ev, resolution='c')
		
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
				
	plt.title("Stations" + ' -- ' + str(len(file_plt)));
	
	x, y = m(float(file_plt[0][10]), float(file_plt[0][9]))
	m.scatter(x, y, 30, color="black", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len(file_plt)):		
		x, y = m(float(file_plt[i][5]), float(file_plt[i][4]))
		m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
								
	plt.savefig(add_save + '/plot_iris' + '.pdf')

###################################################### plot_ray ######################################################

def plot_ray(input, add_ress, add_save):	
	
	"""
	Plot ray path from an event to stations
	"""
	
	fi_plt = open(add_save + '/' + 'plot_file', 'r')
	file_plt = fi_plt.readlines()
	
	for i in range(0, len(file_plt)):
		file_plt[i] = file_plt[i].split(',')
						
	plt.clf()
	
	lat_ev = float(file_plt[0][9])
	lon_ev = float(file_plt[0][10])
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
				
	m = Basemap(projection='moll', lon_0=lon_ev, lat_0=lat_ev, resolution='c')
		
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
				
	plt.title("Ray Path");
	
	x, y = m(float(file_plt[0][10]), float(file_plt[0][9]))
	m.scatter(x, y, 30, color="black", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len(file_plt)):		
		x, y = m(float(file_plt[i][5]), float(file_plt[i][4]))
		m.scatter(x, y, 20, color='red', marker="v", edgecolor="k", zorder=10)
		m.drawgreatcircle(float(file_plt[i][10]), float(file_plt[i][9]), float(file_plt[i][5]), float(file_plt[i][4]), \
			color = 'blue', zorder=2, linestyle='-')
				
	plt.savefig(add_save + '/plot_ray' + '.pdf')

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
	
	m.drawcoastlines()
	m.drawmapboundary() 
	#m.fillcontinents(color='coral',lake_color='aqua')
	m.fillcontinents()
	
	# draw parallels and meridians.
	m.drawparallels(np.arange(-90.,120.,30.))
	m.drawmeridians(np.arange(0.,420.,60.))
	
	#plt.title("Mollweide Projection, Events");
	plt.title("All Events");
	
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len(depth_event)):
		plt.text(x[i], y[i], ' ' + str(depth_event[i]), va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(Address_data + '/Plot_all_events' + '.pdf')

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
