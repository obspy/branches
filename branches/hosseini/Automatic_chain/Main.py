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
- Import required Modules (Python and Obspy)
- Read INPUT file (Parameters)
- Parallel Requests
- Getting list of Events
- Plot all requested events
- 1/2 * IRIS (available stations+waveform)
- 1/2 * Arclink (available stations+waveform)

- Parallel Requests II
- 1/2 * IRIS (available stations+waveform)
- 1/2 * Arclink (available stations+waveform)

- Quality Control
- Updating
- Plotting

- Load events (Lat, Lon and Name of each)
- Load Stations (Lat, Lon and Name of each)
- Plot Ray Paths (event --> stations)
"""


# ------------------------Import required Modules (Python and Obspy)-------------
from obspy.core import read
from obspy.core import UTCDateTime
from lxml import objectify, etree
from datetime import datetime
import pickle
import time
import os
import sys

from read_input import *
from nodes import *
from get_Events import *
#from plot_events import *
from IRIS_get_Network import *
from IRIS_get_Waveform import *
from IRIS_get_Waveform_single import *
from Arclink_get_Network import *
from Arclink_get_Waveform import *
from Arclink_get_Waveform_single import *
from QC_IRIS import *
from QC_ARC import *
from update_IRIS import *
from update_ARC import *
#from plot_IRIS import *
#from plot_ARC import *
#from plot_all_events import *


def Main():
	
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
	
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()

	# ------------------------Parallel Requests--------------------
	if input['nodes'] == 'Y':
		nodes(input)
		
	# ------------------------Getting List of Events---------------------------------
	if input['get_events'] == 'Y':
		(events, len_events, Period, Address_events) = get_Events(input)
	#  CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	if input['plt_event'] == 'on':		
		plot_events(input)

	# ------------------------IRIS------------------------------------------------
	if input['IRIS'] == 'Y':
		
		if input['mass'] ==	'Y':
			
			print '***********************************************************************************************'
			print 'IRIS -- Download all waveforms, Response file and other information based on requested events'
			print '***********************************************************************************************'
				
			(Networks_iris_BHE, Networks_iris_BHN, Networks_iris_BHZ, t_iris) = \
				IRIS_get_Network(input)
					
			IRIS_get_Waveform(input, Networks_iris_BHE,\
			Networks_iris_BHN, Networks_iris_BHZ, t_iris)

		else:		
			
			print '***********************************************************************************************'
			print 'IRIS -- Download single waveform, Response file and other information based on requested events'
			print '***********************************************************************************************'
			
			t_iris = []
			Networks_iris = [input['net'], input['sta'], input['loc'], input['cha']]
			
			for i in range(0, len_events):
				t_iris.append(UTCDateTime(events[i]['datetime']))
					
			IRIS_get_Waveform_single(input, Address_events, len_events, events, Networks_iris, t_iris)

	# ------------------------Arclink------------------------------------------------
	if input['ArcLink'] == 'Y':
		
		if input['mass'] == 'Y':
			
			print '************************************************************************************************'
			print 'ArcLink -- Download all waveforms, Response file and other information based on requested events'
			print '************************************************************************************************'
					
			(Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink) = \
				Arclink_get_Network(input)
		
			Arclink_get_Waveform(input, Nets_Arc_req_BHE, \
				Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink)

		else:
			
			print '**************************************************************************************************'
			print 'ArcLink -- Download single waveform, Response file and other information based on requested events'
			print '**************************************************************************************************'
			
			t_arclink = []
			Networks_ARC = [input['net'], input['sta'], input['loc'], input['cha']]
			
			for i in range(0, len_events):
				t_arclink.append(UTCDateTime(events[i]['datetime']))
			
			Arclink_get_Waveform_single(input, Address_events, len_events, events, Networks_ARC, t_arclink)
				
	# ------------------------Updating--------------------------------
	if input['update_iris'] == 'Y':
		
		print '*********************'
		print 'IRIS -- Updating Mode' + '\n'
		print 'Number of iterations:'
		print input['No_updating_IRIS']
		print '*********************'
		
		for i in range(0, input['No_updating_IRIS']):
			update_IRIS(input)

	if input['update_arc'] == 'Y':
		
		print '************************'
		print 'ArcLink -- Updating Mode' + '\n'
		print 'Number of iterations:'
		print input['No_updating_ARC']
		print '************************'
		
		for i in range(0, input['No_updating_ARC']):
			update_ARC(input)
	
	# ------------------------Quality Control------------------------
	if input['QC_IRIS'] == 'Y':
		
		print '*************************************************************'
		print 'IRIS -- Quality Control (Gap, Timing Quality, Data Quality)'
		print '*************************************************************'

		QC_IRIS(input)
		
	if input['QC_ARC'] == 'Y':
		
		print '****************************************************************'
		print 'ArcLink -- Quality Control (Gap, Timing Quality, Data Quality)'
		print '****************************************************************'
		
		QC_ARC(input)
		
	# ------------------------Plotting--------------------------------
	#CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	if input['plot_all_Events'] == 'Y':
		
		print '*********************'
		print 'Plot all Events'
		print '*********************'
		
		plot_all_events(input)
	#CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	if input['plot_IRIS'] == 'Y':
		
		print '*********************'
		print 'IRIS -- Plotting'
		print '*********************'
		
		plot_IRIS(input)

	if input['plot_ARC'] == 'Y':
		
		print '*********************'
		print 'ArcLink -- Plotting'
		print '*********************'
		
		plot_ARC(input)

	# ---------------------------------------------------------------
	t2_pro = datetime.now()
	t_pro = t2_pro - t1_pro

	print '--------------------------------------------------------------------------------'
	print 'Thanks for using:' + '\n' 
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'ObsPyDMT ' + reset + '(' + bold + 'ObsPy D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' + reset + 'ool)' + reset + '\n'

	print "Total Time:"
	print t_pro
	print '--------------------------------------------------------------------------------'


if __name__ == "__main__":
	status = Main()
	sys.exit(status)

'''

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
