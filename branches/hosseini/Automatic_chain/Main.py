#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import ipdb; ipdb.set_trace()

"""
ObsPyDMT (ObsPy Data Management Tool)

Goal: Management of Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""


"""
- Read INPUT file (Parameters)
- Parallel Requests
- Import required Modules (Python and Obspy)
- Getting list of Events
- Plot all requested events
- IRIS (available stations+waveform)
- Arclink (available stations+waveform)
- Load events (Lat, Lon and Name of each)
- Load Stations (Lat, Lon and Name of each)
- Plot Ray Paths (event --> stations)
"""

# ------------------------Read INPUT file (Parameters)--------------------
from read_input import *
(input) = read_input()

# ------------------------Parallel Requests--------------------
if input['nodes'] == 'Y':
	from nodes import *
	nodes(input)

# ------------------------Import required Modules (Python and Obspy)-------------
from obspy.core import read
from obspy.core import UTCDateTime
from lxml import objectify, etree
from datetime import datetime
from obspy.arclink.client import ArcLinkException as ArcLinkException
import pickle
import time
import os

t1_pro = datetime.now()

print '--------------------------------------------------------------------------------'
bold = "\033[1m"
reset = "\033[0;0m"
print '\t\t' + bold + 'ObsPyDMT ' + reset + '(' + bold + 'ObsPy D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' + reset + 'ool)' + reset + '\n'
print '\t' + 'Automatic tool for Management of Large Seismic Datasets' + '\n'
print ':copyright:'
print 'The ObsPy Development Team (devs@obspy.org)' + '\n'
print ':license:'
print 'GNU Lesser General Public License, Version 3'
print '(http://www.gnu.org/copyleft/lesser.html)'
print '--------------------------------------------------------------------------------'

# ------------------------Getting List of Events---------------------------------
if input['get_events'] == 'Y':
	from get_Events import *
	(events, len_events, Period, Address_events) = get_Events(input)

if input['plt_event'] == 'on':
	from load_event import *
	from plot_all_events import *
	(lat_event, lon_event, name_event) = load_event(len_events, Address_events)	
	
	plot_all_events(input, Address_events, events = events, lon_event = lon_event, \
	lat_event = lat_event, name_event = name_event, len_events = len_events)

# ------------------------IRIS------------------------------------------------
if input['IRIS'] == 'Y':
	
	if input['mass'] ==	'Y':
		
		from IRIS_get_Network import *
		(Networks_iris_BHE, Networks_iris_BHN, Networks_iris_BHZ, t_iris) = \
			IRIS_get_Network(Address_events, len_events, events, input)
		
		from IRIS_get_Waveform import *
		IRIS_get_Waveform(input, Address_events, len_events, events, Networks_iris_BHE,\
		Networks_iris_BHN, Networks_iris_BHZ, t_iris)

	else:
		
		t_iris = []
		Networks_iris = [input['net'], input['sta'], input['loc'], input['cha']]
		
		for i in range(0, len_events):
			t_iris.append(UTCDateTime(events[i]['datetime']))
		
		from IRIS_get_Waveform_single import *
		IRIS_get_Waveform_single(input, Address_events, len_events, events, Networks_iris, t_iris)

# ------------------------Arclink------------------------------------------------
if input['ArcLink'] == 'Y':
	
	if input['mass'] == 'Y':
			
		from Arclink_get_Network import *
		(Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink) = \
			Arclink_get_Network(len_events, events, Address_events)

		from Arclink_get_Waveform import *
		Arclink_get_Waveform(input, Address_events, len_events, events, Nets_Arc_req_BHE, \
			Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink)

	else:
		
		t_arclink = []
		Networks_ARC = [input['net'], input['sta'], input['loc'], input['cha']]
		
		for i in range(0, len_events):
			t_arclink.append(UTCDateTime(events[i]['datetime']))
		
		from Arclink_get_Waveform_single import *
		Arclink_get_Waveform_single(input, Address_events, len_events, events, Networks_ARC, t_arclink)

# ------------------------Quality Control------------------------
if input['QC_IRIS'] == 'Y':
	from QC_IRIS import *
	QC_IRIS(input)

if input['QC_ARC'] == 'Y':
	from QC_ARC import *
	QC_ARC(input)

# ------------------------Updating--------------------------------
if input['update_iris'] == 'Y':
	from update_IRIS import *
	update_IRIS(input)

if input['update_arc'] == 'Y':
	from update_ARC import *
	update_ARC()

# ---------------------------------------------------------------

t2_pro = datetime.now()
t_pro = t2_pro - t1_pro

print "Total Time:"
print t_pro

break_here




# ------------------------Lat, Lon and Name (depth,...) of the events------------
from load_event import *
(lat_event, lon_event, name_event) = load_event(len_events, Address_events)

# ------------------------Lat, Lon and Name of the Stations----------------------
from load_stations import *
(lons_sta_IRIS, lats_sta_IRIS, names_sta_IRIS) = load_stations(Lon = Lon_IRIS, \
	Lat = Lat_IRIS, name = name_IRIS, Len_Lat_Lon = Len_Lat_Lon_IRIS, \
	Num_Event = len_events, Address = Address, Period = Period)

(lons_sta_ARC, lats_sta_ARC, names_sta_ARC) = load_stations(Lon = Lon_ARC, \
	Lat = Lat_ARC, name = name_ARC,	Len_Lat_Lon = Len_Lat_Lon_ARC, \
	Num_Event = len_events, Address = Address, Period = Period)	

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
