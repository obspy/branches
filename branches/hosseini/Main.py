#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Management of Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""


#import ipdb; ipdb.set_trace()

"""
Remaining Parts:
- All available clients: Fissures, Seishub --> check the saved stations 
(save all stations in a file for each web-services)
- Resp file
- Seismogram---PAZ
"""

"""
- Defining the Parameters
- Import required Modules (Python and Obspy)
- Initializing the Clients
- Getting list of Events
- IRIS (available stations+waveform)
- Arclink (available stations+waveform)
- Load events (Lat, Lon and Name of each)
- Load Stations (Lat, Lon and Name of each)
- Plot Ray Paths (event --> stations)
"""

# ------------------------Getting List of Events (Parameters)--------------------
from read_input import *
(Address, min_datetime, max_datetime, min_magnitude, max_magnitude, \
	min_latitude, max_latitude, min_longitude, max_longitude, \
	min_depth, max_depth, max_results, plot_events) = read_input()

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

from obspy.iris import Client as Client_iris
from obspy.neries import Client as Client_neries
from obspy.arclink import Client as Client_arclink

# ------------------------Initializing the Clients-------------------------------
client_iris = Client_iris()
client_neries = Client_neries()
client_arclink = Client_arclink()

# ------------------------Getting List of Events---------------------------------
from get_Events import *
(events, len_events, Period, Address_events) = get_Events(Address, min_datetime, \
		max_datetime, min_magnitude, max_magnitude,	min_latitude, max_latitude, \
		min_longitude, max_longitude, min_depth, max_depth, max_results)
import ipdb; ipdb.set_trace()
if plot_events == 'on':
	from plot_all_events import *
	from load_event import *
	(lat_event, lon_event, name_event) = load_event(len_events, Address_events)
	
	plot_all_events(Address_events, events = events, lon_event = lon_event, \
		lat_event = lat_event, name_event = name_event, Num_Event = len_events)

# ------------------------IRIS------------------------------------------------
from IRIS_get_Network_XML import *
(Networks_iris, t_iris) = \
	IRIS_get_Network_XML(len_events, events, Address, Period)

from IRIS_get_Waveform import *
(Lat_IRIS, Lon_IRIS, name_IRIS, Len_Lat_Lon_IRIS) = \
	IRIS_get_Waveform(Address, Period, len_events, events, Networks_iris, t_iris)

# ------------------------Arclink------------------------------------------------

from Arclink_get_Network import *
(Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink) = \
	Arclink_get_Network(len_events, events, Address, Period)

#break_here

from Arclink_get_Waveform import *
(Lat_ARC, Lon_ARC, name_ARC, Len_Lat_Lon_ARC) = \
	Arclink_get_Waveform(Address, Period, len_events, events, Nets_Arc_req_BHE, \
	Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink, ArcLinkException)

# ------------------------Lat, Lon and Name (depth,...) of the events------------
from load_event import *
(lat_event, lon_event, name_event) = load_event(len_events, Address, Period)

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

plt.savefig(Address + '/Data/figure.pdf')
plt.show()

t2_pro = datetime.now()
t_pro = t2_pro - t1_pro

print "Time:"
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
