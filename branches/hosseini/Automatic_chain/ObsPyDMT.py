#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------
#   Filename:  ObsPyDMT.py
#   Author:    S. Kasra Hosseini zad
#   Email:     hosseini@geophysik.uni-muenchen.de
#
#   Copyright (C) 2011 Seyed Kasra Hosseini zad
#-------------------------------------------------------------------


"""
ObsPyDMT (ObsPy Data Management Tool)

Goal: Management of Large Seismic Datasets

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
- Getting list of Events
- IRIS -- Download all waveforms, Response file and other information based on requested events
- IRIS -- Download single waveform, Response file and other information based on requested events
- ArcLink -- Download all waveforms, Response file and other information based on requested events
- ArcLink -- Download single waveform, Response file and other information based on requested events

- Updating
- Quality Control (Gap, Timing Quality, Data Quality)

- Email
- Report
"""


# ------------------------Import required Modules (Python and Obspy)-------------
from obspy.core import read
from obspy.core import UTCDateTime
from obspy.mseed.libmseed import LibMSEED
from obspy.xseed import Parser

from datetime import datetime
from lxml import etree
import ConfigParser
import commands
import shutil
import pickle
import glob
import sys
import os


from obspy.neries import Client as Client_neries
from obspy.iris import Client as Client_iris
from obspy.arclink import Client as Client_arclink

client_neries = Client_neries()
client_iris = Client_iris()
client_arclink = Client_arclink()

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def ObsPyDMT():
	
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
		get_Events(input)
	
	# ------------------------IRIS------------------------------------------------
	if input['IRIS'] == 'Y':
		
		print '\n' + '***********************************************************************************************'
		print 'IRIS -- Download waveforms, Response file and other information based on requested events'
		print '***********************************************************************************************'
			
		(Stas_iris, t_iris) = IRIS_get_Network(input)
		IRIS_Waveform(input, Stas_iris, t_iris)

	# ------------------------Arclink------------------------------------------------
	if input['ArcLink'] == 'Y':
			
		print '\n' + '************************************************************************************************'
		print 'ArcLink -- Download waveforms, Response file and other information based on requested events'
		print '************************************************************************************************'
				
		(Stas_arc, t_arc) = ARC_get_Network(input)
		ARC_Waveform(input, Stas_arc, t_arc)
				
	# ------------------------Updating--------------------------------
	if input['update_iris'] == 'Y':
		
		print '\n' + '*********************'
		print 'IRIS -- Updating Mode'
		print 'Number of iterations:'
		print input['No_updating_IRIS']
		print '*********************'
		
		for i in range(0, input['No_updating_IRIS']):
			update_IRIS(input)
		

	if input['update_arc'] == 'Y':
		
		print '\n' + '************************'
		print 'ArcLink -- Updating Mode' + '\n'
		print 'Number of iterations:'
		print input['No_updating_ARC']
		print '************************'
		
		for i in range(0, input['No_updating_ARC']):
			update_ARC(input)
	
	# ------------------------Quality Control------------------------
	if input['QC_IRIS'] == 'Y':
		
		print '\n' + '*************************************************************'
		print 'IRIS -- Quality Control (Gap, Timing Quality, Data Quality)'
		print '*************************************************************'

		QC_IRIS(input)
		
	if input['QC_ARC'] == 'Y':
		
		print '\n' + '****************************************************************'
		print 'ArcLink -- Quality Control (Gap, Timing Quality, Data Quality)'
		print '****************************************************************'
		
		QC_ARC(input)
		
	# ------------------------Email--------------------------------
	t2_pro = datetime.now()
	t_pro = t2_pro - t1_pro
	
	if input['email'] == 'Y':
		
		info = commands.getoutput('hostname') + '_' + commands.getoutput('tty')
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		
		i1 = str(info)
		i2 = str(Period)
		i3 = str(t1_pro).split(' ')[0] + '_' + str(t1_pro).split(' ')[1]
		i4 = str(t2_pro).split(' ')[0] + '_' + str(t2_pro).split(' ')[1]
		i5 = str(t_pro)
		if len(i5.split(' ')) == 1:
			i5 = str(t_pro)
		if len(i5.split(' ')) == 3:
			i5 = i5.split(' ')[0] + '_' + i5.split(' ')[1][:-1] + '_' + i5.split(' ')[2]
		
		i6 = str(str(t1_pro.day) + '_' + str(t1_pro.month) + '_' + commands.getoutput('tty'))
		i7 = input['email_address']
		
		commands.getoutput('./email-obspyDMT.sh' + ' ' + i1 + ' ' + i2 + ' ' + i3 + ' ' + i4 + ' ' + i5 + ' ' + i6 + ' ' + i7)
	
	# ------------------------Report--------------------------------	
	if input['report'] == 'Y':
		
		i1 = input['Address']
		i2 = input['Address'] + '/REPORT'
	
		if os.path.exists(i2) == True:
			shutil.rmtree(i2)
			os.makedirs(i2)
			
		else:
			os.makedirs(i2)
		
		commands.getoutput('./REPORT.tcsh' + ' ' + i1 + ' ' + i2)
	
	# --------------------------------------------------------
	print '--------------------------------------------------------------------------------'
	print 'Thanks for using:' + '\n' 
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'ObsPyDMT ' + reset + '(' + bold + 'ObsPy D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' + reset + 'ool)' + reset + '\n'

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
	This module will read the INPUT files which is located in the same folder as NDLB_part_I.py
	"""
	
	config = ConfigParser.RawConfigParser()
	config.read(os.path.join(os.getcwd(), 'INPUT.cfg'))

	input = {}
	input['Address'] = config.get('Address_info', 'address')
	input['inter_address'] = config.get('Address_info', 'interactive_address')
	input['target_folder'] = config.get('Address_info', 'target_folder')
	input['save_folder'] = config.get('Address_info', 'save_folder')
	
	input['min_date'] = config.get('Event_Request', 'min_datetime')
	input['max_date'] = config.get('Event_Request', 'max_datetime')
	input['min_mag'] = config.getfloat('Event_Request', 'min_magnitude')
	input['max_mag'] = config.getfloat('Event_Request', 'max_magnitude')
	input['min_depth'] = config.getfloat('Event_Request', 'min_depth')
	input['max_depth'] = config.getfloat('Event_Request', 'max_depth')
	input['min_lon'] = config.getfloat('Event_Request', 'min_longitude')
	input['max_lon'] = config.getfloat('Event_Request', 'max_longitude')
	input['min_lat'] = config.getfloat('Event_Request', 'min_latitude')
	input['max_lat'] = config.getfloat('Event_Request', 'max_latitude')
	input['t_before'] = config.getfloat('Event_Request', 'time_before')
	input['t_after'] = config.getfloat('Event_Request', 'time_after')
	input['max_result'] = config.getint('Event_Request', 'max_results')
	
	input['get_events'] = config.get('Request', 'get_events')
	input['IRIS'] = config.get('Request', 'IRIS')
	input['ArcLink'] = config.get('Request', 'ArcLink')
	
	input['nodes'] = config.get('Parallel', 'nodes')

	input['waveform'] = config.get('what_to_get', 'waveform')
	input['response'] = config.get('what_to_get', 'response')
	input['SAC'] = config.get('what_to_get', 'SAC')
	
	input['net'] = config.get('specifications_request', 'network')
	input['sta'] = config.get('specifications_request', 'station')
	
	if config.get('specifications_request', 'location') == "''":
		input['loc'] = ''
	elif config.get('specifications_request', 'location') == '""':
		input['loc'] = ''
	else:
		input['loc'] = config.get('specifications_request', 'location')
	
	input['cha'] = config.get('specifications_request', 'channel')
	input['BHE'] = config.get('specifications_request', 'BHE')
	input['BHN'] = config.get('specifications_request', 'BHN')
	input['BHZ'] = config.get('specifications_request', 'BHZ')
	input['other'] = config.get('specifications_request', 'other')
		
	if config.get('specifications_request', 'lat') == 'None':
		input['lat_cba'] = None
	else:
		input['lat_cba'] = config.get('specifications_request', 'lat')
		
	if config.get('specifications_request', 'lon') == 'None':
		input['lon_cba'] = None
	else:
		input['lon_cba'] = config.get('specifications_request', 'lon')
	
	if config.get('specifications_request', 'minradius') == 'None':
		input['mr_cba'] = None
	else:
		input['mr_cba'] = config.get('specifications_request', 'minradius')
	
	if config.get('specifications_request', 'maxradius') == 'None':
		input['Mr_cba'] = None
	else:
		input['Mr_cba'] = config.get('specifications_request', 'maxradius')
	
		
	if config.get('specifications_request', 'minlat') == 'None':
		input['mlat_rbb'] = None
	else:
		input['mlat_rbb'] = config.get('specifications_request', 'minlat')
	
	if config.get('specifications_request', 'maxlat') == 'None':
		input['Mlat_rbb'] = None
	else:
		input['Mlat_rbb'] = config.get('specifications_request', 'maxlat')
	
	if config.get('specifications_request', 'minlon') == 'None':
		input['mlon_rbb'] = None
	else:
		input['mlon_rbb'] = config.get('specifications_request', 'minlon')
	
	if config.get('specifications_request', 'maxlon') == 'None':
		input['Mlon_rbb'] = None
	else:
		input['Mlon_rbb'] = config.get('specifications_request', 'maxlon')

	
	input['TEST'] = config.get('test', 'TEST')
	input['TEST_no'] = config.getint('test', 'TEST_no')
	
	input['update_interactive'] = config.get('update', 'update_interactive')
	input['update_iris'] = config.get('update', 'update_iris')
	input['update_arc'] = config.get('update', 'update_arc')
	input['No_updating_IRIS'] = config.getint('update', 'num_updating_IRIS')
	input['No_updating_ARC'] = config.getint('update', 'num_updating_ARC')

	input['QC_IRIS'] = config.get('QC', 'QC_IRIS')
	input['QC_ARC'] = config.get('QC', 'QC_ARC')
	
	input['email'] = config.get('email', 'email')
	input['email_address'] = config.get('email', 'email_address')
	
	input['report'] = config.get('report', 'report')
	
	input['plt_event'] = config.get('ObsPyPT', 'plot_event')
	input['plt_sta'] = config.get('ObsPyPT', 'plot_sta')
	input['plt_ray'] = config.get('ObsPyPT', 'plot_ray')

	input['llcrnrlon'] = config.getfloat('ObsPyPT', 'llcrnrlon')
	input['urcrnrlon'] = config.getfloat('ObsPyPT', 'urcrnrlon')
	input['llcrnrlat'] = config.getfloat('ObsPyPT', 'llcrnrlat')
	input['urcrnrlat'] = config.getfloat('ObsPyPT', 'urcrnrlat')
	
	input['lon_0'] = config.getfloat('ObsPyPT', 'lon_0')
	input['lat_0'] = config.getfloat('ObsPyPT', 'lat_0')
		
	return input
	
###################################################### nodes ######################################################

def nodes(input):
	
	"""
	Downloading in Parallel way
	Please change the 'INPUT-Periods' file for different requests
	Suggestion: Do not request more than 10 in parallel...
	"""
	
	f = open(os.path.join(os.getcwd(), 'INPUT-Periods'))
	per_tty = f.readlines()
	
	for i in range(0, len(per_tty)):
		per_tty[i] = per_tty[i].split('_')
	
	if os.path.exists(input['Address'] + '/tty-info') != True:
	
		if os.path.exists(input['Address']) != True:
			os.makedirs(input['Address'])
		
		print '\n' + '-------------------------------------------------------------'
		n = int(raw_input('Please enter a node number: (from 0 to ... depends on INPUT-Periods.)' + '\n'))
		print '-------------------------------------------------------------'
		
		tty = open(input['Address'] + '/tty-info', 'w')
		
		tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
			'_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + per_tty[n][3][:-1] + '  ,  ' +  '\n')
		
		tty.close()		
		
	else:
		
		print '\n' + '-------------------------------------------------------------'
		n = int(raw_input('Please enter a node number: (from 0 to ... depends on INPUT-Periods.)' + '\n' + '(If you enter "-1", it means that the node number already exists in the "tty-info" file.)' + '\n'))
		print '-------------------------------------------------------------'
		
		if n == -1:
			print 'You entered "-1" -- the node number exists in the tty-info!'
			print '-------------------------------------------------------------'
		else: 
			tty = open(input['Address'] + '/tty-info', 'a')
			tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
					'_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + per_tty[n][3][:-1] + '  ,  ' +  '\n')

			tty.close()		
	
	
	Address_data = input['Address']
	
	tty = open(input['Address'] + '/tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				
				input['min_date'] = tty_str[i][2].split('_')[0]
				input['max_date'] = tty_str[i][2].split('_')[1]
				input['min_mag'] = tty_str[i][2].split('_')[2]
				input['max_mag'] = tty_str[i][2].split('_')[3]
					
	return input

###################################################### get_Events ######################################################

def get_Events(input):
	
	"""
	Getting list of events from NERIES
	NERIES: a client for the Seismic Data Portal (http://www.seismicportal.eu)
	"""
	
	t_event_1 = datetime.now()
			
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	
	Address_events = input['Address'] + '/' + Period
	
	if os.path.exists(Address_events) == True:
		print '\n' + '-------------------------------------------------------------'
		
		if raw_input('Folder for requested Period [' + str(Address_events) + '] ' + '\n' + 'exists in your directory.' + '\n\n' + \
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
	
	
	events = client_neries.getEvents(min_datetime=input['min_date'], max_datetime=input['max_date'], \
		min_magnitude=input['min_mag'], max_magnitude=input['max_mag'], \
		min_latitude=input['min_lat'], max_latitude=input['max_lat'], \
		min_longitude=input['min_lon'], max_longitude=input['max_lon'], \
		min_depth = input['min_depth'], max_depth=input['max_depth'], max_results=input['max_result'])
		
	
	os.makedirs(Address_events + '/EVENT')
	
	len_events = len(events)
	
	print 'Length of the events found based on the inputs: ' + str(len_events) + '\n'
	
	Events_No = []

	for i in range(0, len_events):
		Events_No.append(i+1)
		print "Event No:" + " " + str(i)
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
	#Event_cat.writelines('Number of Events: ' + str(i) + '\n')
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
	
	Event_file = open(Address_events + '/EVENT/event_list', 'w')
	pickle.dump(events, Event_file)
	Event_file.close()
		
	print 'Events are saved!'
	
	print 'Length of events: ' + str(len_events) + '\n'
	
	t_event_2 = datetime.now()
	t_event = t_event_2 - t_event_1
	
	print 'Time for getting and saving the events:'
	print t_event

###################################################### IRIS_get_Network ######################################################

def IRIS_get_Network(input):
	
	"""
	Returns available IRIS stations at the IRIS-DMC for all requested events
	"""
	
	t_iris_1 = datetime.now()
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	for i in range(0, len_events):
		if os.path.exists(Address_events + '/' + events[i]['event_id'] + '/IRIS') == True:
			
			if raw_input('Folder for IRIS -- requested Period (min/max) and Magnitude (min/max) -- exists in your directory.' + '\n\n' + \
			'You could either close the program and try updating your folder OR remove the tree, continue the program and download again.' + \
			'\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
				print '-------------------------------------------------------------'
				shutil.rmtree(Address_events + '/' + events[i]['event_id'] + '/IRIS')
			
			else:
				print '-------------------------------------------------------------'
				print 'So...you decided to update your folder...Ciao'
				print '-------------------------------------------------------------'
				sys.exit()
	
	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/BH_RAW/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/Resp/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/info/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS/Excep_py/')
	
	print "-------------------------------------------------"
	print 'IRIS-Folders are Created!'
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/Excep_py/' + 'excep_avail', 'w')
		Report = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/info/' + 'report_st', 'w')
		Exception_file.close()
		Report.close()
	
	t = []
	Stas = []
	
	for i in range(0, len_events):
		
		t.append(UTCDateTime(events[i]['datetime']))
		
		try:		
			
			Result = client_iris.availability(network=input['net'], station=input['sta'], location=input['loc'], channel=input['cha'], \
				starttime=t[i]-10, endtime=t[i]+10, lat=input['lat_cba'], lon=input['lon_cba'], minradius=input['mr_cba'], \
				maxradius=input['Mr_cba'], minlat=input['mlat_rbb'], maxlat=input['Mlat_rbb'], \
				minlon=input['mlon_rbb'], maxlon=input['Mlon_rbb'], output='bulk')
			
			R = Result.splitlines()
			Stas.append(R)
			
			print 'IRIS-Availability for event: ' + str(i) + '  --->' + 'DONE'

		except Exception, e:
				
			Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/IRIS/Excep_py/' + 'excep_avail', 'a')
			ee = 'Event:' + str(i) + '---' + str(e) + '\n'
			
			Exception_file.writelines(ee)
			Exception_file.close()
			print e			

	
	Stas_iris = []
	
	for i in range(0, len_events):
		sta = []
		for j in range(0, len(Stas[i])):
			sta.append(Stas[i][j].split(' '))
		Stas_iris.append(sta)


	t_iris_2 = datetime.now()
	t_iris = t_iris_2 - t_iris_1
	
	print "--------------------"
	print 'IRIS-Time: (Availability)'
	print t_iris	
	
	return Stas_iris, t
	#Sta_BHE, Sta_BHN, Sta_BHZ, 
	
###################################################### IRIS_Waveform ######################################################

def IRIS_Waveform(input, Stas_iris, t):
	
	"""
	Gets Waveforms, Response files and other information from IRIS web-service based on the requested events...
	"""
	
	if input['BHE'] == 'Y':
		Sta_req = IRIS_folder_sta_initialize(input, Stas_iris, channel = 'BHE')
		IRIS_get_Waveform(input, Sta_req, channel = 'BHE', interactive = 'N', type = 'save')
	
	if input['BHN'] == 'Y':
		Sta_req = IRIS_folder_sta_initialize(input, Stas_iris, channel = 'BHN')
		IRIS_get_Waveform(input, Sta_req, channel = 'BHN', interactive = 'N', type = 'save')
	
	if input['BHZ'] == 'Y':
		Sta_req = IRIS_folder_sta_initialize(input, Stas_iris, channel = 'BHZ')
		IRIS_get_Waveform(input, Sta_req, channel = 'BHZ', interactive = 'N', type = 'save')
	
	if input['other'] == 'Y':
		Sta_req = IRIS_folder_sta_initialize(input, Stas_iris, channel = input['cha'])
		IRIS_get_Waveform(input, Sta_req, channel = input['cha'], interactive = 'N', type = 'save')

	print "-------------------------------------------------"
	print 'IRIS is DONE'
	print "-------------------------------------------------"

###################################################### IRIS_folder_sta_initialize ######################################################

def IRIS_folder_sta_initialize(input, Stas_iris, channel):
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	Sta_req = []

	for i in range(0, len_events):
		sta_req = []
		for j in range(0, len(Stas_iris[i])):
			if Stas_iris[i][j][3] == channel:
				sta_req.append(Stas_iris[i][j])
		Sta_req.append(sta_req)


	for i in range(0, len_events):
		Sta_req_target = Sta_req[i]
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/info/' + 'all_iris_' + channel, 'w')
		pickle.dump(Sta_req_target, Station_file)
		Station_file.close()
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/Excep_py/' + 'excep_iris_' + channel, 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------IRIS----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/info/' + 'avail_iris_' + channel, 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/IRIS/info/' + 'iris_' + channel, 'w')
		Syn_file.close()
	
	return Sta_req

###################################################### IRIS_get_Waveform ######################################################

def IRIS_get_Waveform(input, Sta_req, channel, interactive, type):
	
	t_wave_1 = datetime.now()
	
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter

	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	t = []
	
	for i in range(0, len_events):
		t.append(UTCDateTime(events[i]['datetime']))
	
	for i in range(0, len_events):
		print "--------------------"
		if input['TEST'] == 'Y':
			len_req_iris = input['TEST_no']

		else:	
			len_req_iris = len(Sta_req[i])

		dic = {}				
			
		for j in range(0, len_req_iris):
		
			print '------------------'
			print type
			print 'IRIS-Event and Station Numbers are:'
			print str(i) + '-' + str(j+1) + '/' + str(len(Sta_req[i])) + '-' + channel
			try:
				
				client_iris = Client_iris()
	
				if input['waveform'] == 'Y':					
					
					dummy = 'Waveform'
					
					client_iris.saveWaveform(Address_events + '/' + events[i]['event_id'] +\
						'/IRIS/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel, Sta_req[i][j][0], Sta_req[i][j][1], \
						Sta_req[i][j][2], channel, t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel + "  ---> DONE"  
				
				if input['response'] == 'Y':

					dummy = 'Response'
					
					client_iris.saveResponse(Address_events + '/' +	events[i]['event_id'] + \
						'/IRIS/Resp/' + 'RESP' + '.' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel, Sta_req[i][j][0], Sta_req[i][j][1], \
						Sta_req[i][j][2], channel, t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Response for: " + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel + "  ---> DONE"
					
					'''
					dummy = 'sacpz'
					
					import ipdb; ipdb.set_trace()
					
					sacpz = client_iris.sacpz(network=Sta_req[i][j][0], \
						station=Sta_req[i][j][1], location=Sta_req[i][j][2], \
						channel=channel, starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
				dummy = 'availability'
				
				avail = client_iris.availability(network=Sta_req[i][j][0], \
					station=Sta_req[i][j][1], location=Sta_req[i][j][2], \
					channel=channel, starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'], output = 'xml')
				
				
				xml_doc = etree.fromstring(avail)
						
				#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
				#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
				Sta_net_code = xml_doc.xpath('/StaMessage/Station')[0].get('net_code')
				Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[0].get('sta_code')
				Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[0].text
				Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[0].text
				Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[0].text
				Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('loc_code')
				Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[0].get('chan_code')
				#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
				#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
				#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
				#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
				#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
				#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
				#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
				#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
				dic[j] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
					'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
					'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
				
				if input['SAC'] == 'Y':
					
					st = read(Address_events + '/' + events[i]['event_id'] +\
							'/IRIS/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel)
					st[0].write(Address_events + '/' + events[i]['event_id'] +\
							'/IRIS/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel, 'SAC')
					st = read(Address_events + '/' + events[i]['event_id'] +\
							'/IRIS/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel)
					
					st[0].stats['sac']['stla'] = dic[j]['Latitude']
					st[0].stats['sac']['stlo'] = dic[j]['Longitude']
					st[0].stats['sac']['stel'] = dic[j]['Elevation']
					
					st[0].stats['sac']['evla'] = events[i]['latitude']
					st[0].stats['sac']['evlo'] = events[i]['longitude']
					st[0].stats['sac']['evdp'] = events[i]['depth']
					st[0].stats['sac']['mag'] = events[i]['magnitude']
					
					st[0].write(Address_events + '/' + events[i]['event_id'] +\
							'/IRIS/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel, 'SAC')

				Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
					'/IRIS/info/' + 'iris_' + channel, 'a')
				syn = dic[j]['Network'] + ',' + dic[j]['Station'] + ',' + \
					dic[j]['Location'] + ',' + dic[j]['Channel'] + ',' + dic[j]['Latitude'] + \
					',' + dic[j]['Longitude'] + ',' + dic[j]['Elevation'] + ',' + '0' + ',' + events[i]['event_id'] + ',' + str(events[i]['latitude']) \
					 + ',' + str(events[i]['longitude']) + ',' + str(events[i]['depth']) + ',' + str(events[i]['magnitude']) + ',' + '\n'
				Syn_file.writelines(syn)
				Syn_file.close()
				
				print "Saving Station  for: " + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
					Sta_req[i][j][2] + '.' + channel + "  ---> DONE"
				
				Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/info/' + 'avail_iris_' + channel, 'a')
				pickle.dump(dic[j], Station_file)
				Station_file.close()
				
			except Exception, e:	
				
				print dummy + '---' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + \
					'.' +Sta_req[i][j][2] + '.' + channel
				
				Exception_file = open(Address_events + '/' + \
					events[i]['event_id'] + '/IRIS/Excep_py/' + 'excep_iris_' + channel, 'a')

				ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Sta_req[i][j][0] + \
					'.' + Sta_req[i][j][1] + '.' + \
					Sta_req[i][j][2] + '.' + channel + \
					'---' + str(e) + '\n'
				
				Exception_file.writelines(ee)
				Exception_file.close()
				print e	
			
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/info/' + 'report_st', 'a')
		eventsID = events[i]['event_id']
		Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
		Report.writelines(eventsID + '\n')
		Report.writelines('---------------IRIS---------------' + '\n')
		Report.writelines('---------------' + channel + '---------------' + '\n')
		rep = 'IRIS-Available stations for channel ' + channel + ' and for event' + '-' + str(i) + ': ' + str(len(Sta_req[i])) + '\n'
		Report.writelines(rep)
		rep = 'IRIS-' + type + ' stations for channel ' + channel + ' and for event' + '-' + str(i) + ':     ' + str(len(dic)) + '\n'
		Report.writelines(rep)
		Report.writelines('----------------------------------' + '\n')
			
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
			
		rep = "Time for " + type + "ing Waveforms from IRIS: " + str(t_wave) + '\n'
		Report.writelines(rep)
		Report.writelines('----------------------------------' + '\n')
		Report.close()

###################################################### get_address ######################################################

def get_address():
	
	"""
	This program gets the address for next steps...
	"""
	
	print '----------------------------------------------------'
	address = raw_input('Please enter the target address:' + '\n')
	print '----------------------------------------------------'
			
	return address

###################################################### Arclink_get_Network ######################################################

def ARC_get_Network(input):
	
	"""
	Returns available Arclink stations for all requested events
	-----------------
	Problems:
	- ['BW', 'WETR', '', 'BH*']
	"""
		
	t_arc_1 = datetime.now()

	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	for i in range(0, len_events):
		if os.path.exists(Address_events + '/' + events[i]['event_id'] + '/ARC') == True:
			
			if raw_input('Folder for ARC -- requested Period (min/max) and Magnitude (min/max) exists in your directory.' + '\n\n' + \
			'You could either close the program and try updating your folder OR remove the tree, continue the program and download again.' + \
			'\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
				print '-------------------------------------------------------------'
				shutil.rmtree(Address_events + '/' + events[i]['event_id'] + '/ARC')

			else:
				print '-------------------------------------------------------------'
				print 'So...you decided to update your folder...Ciao'
				print '-------------------------------------------------------------'
				sys.exit()

	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/BH_RAW/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/Resp/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/info/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/Excep_py/')
	
	print "-------------------------------------------------"
	print 'ArcLink-Folders are Created!'


	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/Excep_py/' + 'excep_avail', 'w')
		Report = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'report_st', 'w')
		Exception_file.close()
		Report.close()
	
	
	t = []
	Stas = []

	for i in range(0, len_events):
		
		t.append(UTCDateTime(events[i]['datetime']))
	
		try:
			
			Stas.append(client_arclink.getNetworks(t[i]-10, t[i]+10))
			print 'ArcLink-Availability for event: ' + str(i) + '  --->' + 'DONE'

		except Exception, e:
				
			Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/Excep_py/' + 'excep_avail', 'a')
			ee = 'Event:' + str(i) + '---' + str(e) + '\n'
			
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
	
	Stas_arc = []
	
	for i in range(0, len_events):
		stas_arc = []
		for j in range(0, len(Stas[i].keys())):
			Stas_tmp = Stas[i].keys()[j].split('.')
			if len(Stas_tmp) == 4:
				stas_arc.append(Stas_tmp)
		
		Stas_arc.append(stas_arc)
		Stas_arc[i].sort()
			
	t_arc_2 = datetime.now()
	t_arc_21 = t_arc_2 - t_arc_1
	
	print "--------------------"
	print 'ARC-Time: (Availability)'
	print t_arc_21
	
	return Stas_arc, t

###################################################### ARC_Waveform ######################################################

def ARC_Waveform(input, Stas_arc, t):
	
	"""
	Gets Waveforms, Response files and other information from ArcLink based on the requested events...
	"""
	
	if input['BHE'] == 'Y':
		Sta_req = ARC_folder_sta_initialize(input, Stas_arc, channel = 'BHE')
		ARC_get_Waveform(input, Sta_req, channel = 'BHE', interactive = 'N', type = 'save')
	
	if input['BHN'] == 'Y':
		Sta_req = ARC_folder_sta_initialize(input, Stas_arc, channel = 'BHN')
		ARC_get_Waveform(input, Sta_req, channel = 'BHN', interactive = 'N', type = 'save')
	
	if input['BHZ'] == 'Y':
		Sta_req = ARC_folder_sta_initialize(input, Stas_arc, channel = 'BHZ')
		ARC_get_Waveform(input, Sta_req, channel = 'BHZ', interactive = 'N', type = 'save')
	
	if input['other'] == 'Y':
		Sta_req = ARC_folder_sta_initialize(input, Stas_arc, channel = input['cha'])
		ARC_get_Waveform(input, Sta_req, channel = input['cha'], interactive = 'N', type = 'save')

	print "-------------------------------------------------"
	print 'ArcLink is DONE'
	print "-------------------------------------------------"

###################################################### ARC_folder_sta_initialize ######################################################

def ARC_folder_sta_initialize(input, Stas_arc, channel):
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	Sta_req = []

	for i in range(0, len_events):
		sta_req = []
		for j in range(0, len(Stas_arc[i])):
			if Stas_arc[i][j][3] == channel:
				sta_req.append(Stas_arc[i][j])
		Sta_req.append(sta_req)


	for i in range(0, len_events):
		Sta_req_target = Sta_req[i]
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'all_arc_' + channel, 'w')
		pickle.dump(Sta_req_target, Station_file)
		Station_file.close()
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/Excep_py/' + 'excep_arc_' + channel, 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'avail_arc_' + channel, 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'arc_' + channel, 'w')
		Syn_file.close()
	
	return Sta_req

###################################################### Arclink_get_Waveform ######################################################

def ARC_get_Waveform(input, Sta_req, channel, interactive, type):
	
	"""
	Gets Waveforms, Response files and other information from ArcLink based on the requested events...
	-----------------
	Problems:
	- Client_arclink(command_delay=0.1)
	"""
	
	t_wave_1 = datetime.now()
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	t = []
	
	for i in range(0, len_events):
		t.append(UTCDateTime(events[i]['datetime']))
	
	for i in range(0, len_events):
		print "--------------------"
		if input['TEST'] == 'Y':
			len_req_arc = input['TEST_no']
			
		else:	 
			len_req_arc = len(Sta_req[i]) 		
		

		inv = {}
			
		for j in range(0, len_req_arc):
		
			print '------------------'
			print type
			print 'ArcLink-Event and Station Numbers are:'
			print str(i) + '-' + str(j+1) + '/' + str(len(Sta_req[i])) + '-' + channel
			
			try:
				
				client_arclink = Client_arclink(timeout=5)
				
				if input['waveform'] == 'Y':
						
					dummy = 'Waveform'
					
					client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel, Sta_req[i][j][0], Sta_req[i][j][1], \
						Sta_req[i][j][2], channel, t[i]-input['t_before'], t[i]+input['t_after'])
					
					print "Saving Waveform for: " + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel + "  ---> DONE"  
					
				
				if input['response'] == 'Y':
						
					dummy = 'Response'
					
					client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/Resp/' + 'RESP' + '.' + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel, Sta_req[i][j][0], Sta_req[i][j][1], \
						Sta_req[i][j][2], channel, t[i]-input['t_before'], t[i]+input['t_after'])
					
					sp = Parser(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/Resp/' + 'RESP' + '.' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel)
					
					sp.writeRESP(Address_events + '/' + events[i]['event_id'] + '/ARC/Resp')
					
					'''
					pars = Parser()
						
					pars.read(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/Resp/' + 'RESP' + '.' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel)
					
					pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/Resp/' + 'RESP' + '.' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel)
					'''
				
					print "Saving Response for: " + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
						Sta_req[i][j][2] + '.' + channel + "  ---> DONE"
						
				
				dummy = 'Inventory'
				
				inv[j] = client_arclink.getInventory(Sta_req[i][j][0], Sta_req[i][j][1], \
					Sta_req[i][j][2], channel)
				
				dum = Sta_req[i][j][0] + '.' + Sta_req[i][j][1]
				
				if input['SAC'] == 'Y':
							
					st = read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel)
					st[0].write(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel, 'SAC')
					st = read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel)
					
					if inv[j][dum]['latitude'] != None:
						st[0].stats['sac']['stla'] = inv[j][dum]['latitude']
					if inv[j][dum]['longitude'] != None:
						st[0].stats['sac']['stlo'] = inv[j][dum]['longitude']
					if inv[j][dum]['elevation'] != None:
						st[0].stats['sac']['stel'] = inv[j][dum]['elevation']
					if inv[j][dum]['depth'] != None:
						st[0].stats['sac']['stdp'] = inv[j][dum]['depth']
					
					st[0].stats['sac']['evla'] = events[i]['latitude']
					st[0].stats['sac']['evlo'] = events[i]['longitude']
					st[0].stats['sac']['evdp'] = events[i]['depth']
					st[0].stats['sac']['mag'] = events[i]['magnitude']
					
					st[0].write(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
							Sta_req[i][j][2] + '.' + channel, 'SAC')

				Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
					'/ARC/info/' + 'arc_' + channel, 'a')
				syn = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
					Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + str(inv[j][dum]['latitude']) + \
					',' + str(inv[j][dum]['longitude']) + ',' + str(inv[j][dum]['elevation']) + ',' + \
					str(inv[j][dum]['depth']) + ',' + events[i]['event_id'] + ',' + str(events[i]['latitude']) \
					 + ',' + str(events[i]['longitude']) + ',' + str(events[i]['depth']) + ',' + str(events[i]['magnitude']) + ',' + '\n'
				Syn_file.writelines(syn)
				Syn_file.close()
				
				print "Saving Station  for: " + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + '.' + \
					Sta_req[i][j][2] + '.' + channel + "  ---> DONE"
				
				Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'avail_arc_' + channel, 'a')
				pickle.dump(inv[j], Station_file)
				Station_file.close()
				
			except Exception, e:	
				
				print dummy + '---' + Sta_req[i][j][0] +	'.' + Sta_req[i][j][1] + \
					'.' +Sta_req[i][j][2] + '.' + channel
				
				Exception_file = open(Address_events + '/' + \
					events[i]['event_id'] + '/ARC/Excep_py/' + 'excep_arc_' + channel, 'a')

				ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Sta_req[i][j][0] + \
					'.' + Sta_req[i][j][1] + '.' + Sta_req[i][j][2] + '.' + channel + \
					'---' + str(e) + '\n'
				
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
							
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		eventsID = events[i]['event_id']
		Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
		Report.writelines(eventsID + '\n')
		Report.writelines('---------------ARC---------------' + '\n')
		Report.writelines('---------------' + channel + '---------------' + '\n')
		rep = 'ARC-Available stations for channel ' + channel + ' and for event' + '-' + str(i) + ': ' + str(len(Sta_req[i])) + '\n'
		Report.writelines(rep)
		rep = 'ARC-' + type + ' stations for channel ' + channel + ' and for event' + '-' + str(i) + ':     ' + str(len(inv)) + '\n'
		Report.writelines(rep)
		Report.writelines('----------------------------------' + '\n')
		
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
		
		rep = "Time for " + type + "ing Waveforms from ArcLink: " + str(t_wave) + '\n'
		Report.writelines(rep)
		Report.writelines('----------------------------------' + '\n')
		Report.close()

###################################################### update_IRIS ######################################################

def update_IRIS(input):
	
	"""
	Updating the station folders from IRIS web-service
	Attention: This module update all station folders for all events in one directory.
	-----------------
	Problems:
	- excep_iris_update OR excep_iris?
	"""

	if input['BHE'] == 'Y':
		Sta_req = update_req_sta_IRIS(input, channel = 'BHE', interactive = input['inter_address'])
		IRIS_get_Waveform(input, Sta_req, channel = 'BHE', interactive = 'N', type = 'update')
	
	if input['BHN'] == 'Y':
		Sta_req = update_req_sta_IRIS(input, channel = 'BHN', interactive = input['inter_address'])
		IRIS_get_Waveform(input, Sta_req, channel = 'BHN', interactive = 'N', type = 'update')
	
	if input['BHZ'] == 'Y':
		Sta_req = update_req_sta_IRIS(input, channel = 'BHZ', interactive = input['inter_address'])
		IRIS_get_Waveform(input, Sta_req, channel = 'BHZ', interactive = 'N', type = 'update')

	print "-------------------------------------------------"
	print 'IRIS-Update is DONE'
	print "-------------------------------------------------"
	
###################################################### update_req_sta_IRIS ######################################################
	
def update_req_sta_IRIS(input, channel, interactive = 'N'):
	
	t_update_1 = datetime.now()
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter

	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
			
	all_iris = []
	saved_iris = []
	
	for l in range(0, len_events):
		
		ls_all_stas = \
			open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/all_iris_' + channel, 'r')
		all_iris_tmp = pickle.load(ls_all_stas)
		ls_all_stas.close()
				
		for i in range(0, len(all_iris_tmp)):
			all_iris_tmp[i] = str(all_iris_tmp[i][0] + '_' + all_iris_tmp[i][1] + '_' +\
				all_iris_tmp[i][2] + '_' + all_iris_tmp[i][3])	
		
		all_iris.append(all_iris_tmp)
		
		
		ls_saved_stas = \
			open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/iris_' + channel, 'r')
		saved_stas = ls_saved_stas.readlines()
		
		for i in range(0, len(saved_stas)):
			saved_stas[i] = saved_stas[i].split(',')
			if saved_stas[i][2] == '  ':
				saved_stas[i][2] = '--'
			saved_stas[i] = str(saved_stas[i][0] + '_' + saved_stas[i][1] + '_' + \
				saved_stas[i][2] + '_' + saved_stas[i][3])
		
		saved_iris.append(saved_stas)
	
	Stas_req = []
	for l in range(0, len_events):
		diff_tmp = set(all_iris[l]).difference(set(saved_iris[l])) 
		Stas_req.append(list(diff_tmp))
		
		for m in range(0, len(Stas_req[l])):
			Stas_req[l][m] = Stas_req[l][m].split('_')
		
		Stas_req[l].sort()
	
	return Stas_req
	
		
	import ipdb; ipdb.set_trace()
		

###################################################### update_ARC ######################################################

def update_ARC(input):
	
	"""
	Updating the station folders from IRIS web-service
	Attention: This module update all station folders for all events in one directory.
	-----------------
	Problems:
	- excep_iris_update OR excep_iris?
	"""

	if input['BHE'] == 'Y':
		Sta_req = update_req_sta_ARC(input, channel = 'BHE', interactive = input['inter_address'])
		ARC_get_Waveform(input, Sta_req, channel = 'BHE', interactive = 'N', type = 'update')
	
	if input['BHN'] == 'Y':
		Sta_req = update_req_sta_ARC(input, channel = 'BHN', interactive = input['inter_address'])
		ARC_get_Waveform(input, Sta_req, channel = 'BHN', interactive = 'N', type = 'update')
	
	if input['BHZ'] == 'Y':
		Sta_req = update_req_sta_ARC(input, channel = 'BHZ', interactive = input['inter_address'])
		ARC_get_Waveform(input, Sta_req, channel = 'BHZ', interactive = 'N', type = 'update')

	print "-------------------------------------------------"
	print 'ArcLink-Update is DONE'
	print "-------------------------------------------------"
	
###################################################### update_req_sta_ARC ######################################################
	
def update_req_sta_ARC(input, channel, interactive = 'N'):
	
	t_update_1 = datetime.now()
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter

	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
			
	all_arc = []
	saved_arc = []
	
	for l in range(0, len_events):
		
		ls_all_stas = \
			open(Address_events + '/' + events[l]['event_id'] + '/ARC/info/all_arc_' + channel, 'r')
		all_arc_tmp = pickle.load(ls_all_stas)
		ls_all_stas.close()
				
		for i in range(0, len(all_arc_tmp)):
			all_arc_tmp[i] = str(all_arc_tmp[i][0] + '_' + all_arc_tmp[i][1] + '_' +\
				all_arc_tmp[i][2] + '_' + all_arc_tmp[i][3])	
		
		all_arc.append(all_arc_tmp)
		
		
		ls_saved_stas = \
			open(Address_events + '/' + events[l]['event_id'] + '/ARC/info/arc_' + channel, 'r')
		saved_stas = ls_saved_stas.readlines()
		
		for i in range(0, len(saved_stas)):
			saved_stas[i] = saved_stas[i].split(',')
			if saved_stas[i][2] == '  ':
				saved_stas[i][2] = '--'
			saved_stas[i] = str(saved_stas[i][0] + '_' + saved_stas[i][1] + '_' + \
				saved_stas[i][2] + '_' + saved_stas[i][3])
		
		saved_arc.append(saved_stas)
	
	Stas_req = []
	for l in range(0, len_events):
		diff_tmp = set(all_arc[l]).difference(set(saved_arc[l])) 
		Stas_req.append(list(diff_tmp))
		
		for m in range(0, len(Stas_req[l])):
			Stas_req[l][m] = Stas_req[l][m].split('_')
		
		Stas_req[l].sort()
	
	return Stas_req

###################################################### QC_IRIS ######################################################

def QC_IRIS(input):
	
	"""
	Quality Control (Gap, Timing Quality, Data Quality) for IRIS stations.
	"""
		
	Address_data = input['Address']
	
	pre_ls_event = []
	
	tty = open(input['Address'] + '/tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				pre_ls_event.append(Address_data + '/' + tty_str[i][2])
	
	
	for i in range(0, len(pre_ls_event)):
		print 'Quality Check for: ' + '\n' + str(pre_ls_event[i])
	print '*************************************************************'
	
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
	
	add_IRIS_QC = []
	
	for i in ls_event:
		add_IRIS_QC.append(i + '/IRIS/QC')
		
	add_IRIS_events = []
	for i in pre_ls_event:
		add_IRIS_events.append(i + '/EVENT/event_list')
		
	events_all = []
	
	for i in add_IRIS_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
	
	for l in range(0, len(events_all)):
		
		events = pickle.load(events_all[l])
		len_events = len(events)
		
		for k in range(0, len_events):
		
			if os.path.exists(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/QC/') == True:
				
				shutil.rmtree(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/QC/')
				os.makedirs(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/QC/')
				
			else:
				os.makedirs(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/QC/')	

		for k in range(0, len_events):
		
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/IRIS/QC/' + 'GAP', 'w')
			eventsID = events[k]['event_id']
			gapfile.writelines('\n' + eventsID + '\n')
			gapfile.writelines('----------------------------IRIS----------------------------'+ '\n')
			gapfile.writelines('----------------------------GAP----------------------------'+ '\n')
			gapfile.close()
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/IRIS/QC/' + 'TimingQuality', 'w')
			eventsID = events[k]['event_id']
			timefile.writelines('\n' + eventsID + '\n')
			'''
			timefile.writelines('\n' + '----------------------------------' + '\n')
			timefile.writelines('Description:' + '\n')
			timefile.writelines('timing quality in percent (0-100).' + '\n')
			timefile.writelines('0: the timing is completely unreliable' + '\n')
			'''
			timefile.writelines('----------------------------IRIS----------------------------'+ '\n')
			timefile.writelines('----------------------------TIMEQ----------------------------'+ '\n')
			timefile.close()
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/IRIS/QC/' + 'DataQuality', 'w')
			eventsID = events[k]['event_id']
			datafile.writelines('\n' + eventsID + '\n')
			'''
			datafile.writelines('\n' + '----------------------------------' + '\n')
			datafile.writelines('Description:' + '\n')
			datafile.writelines('Counts all data quality flags of the given MiniSEED file. This method will count all set data quality' + '\n' + 
				'flag bits in the fixed section of the data header in a MiniSEED file and returns the total count for each flag type.' + '\n' + 'Data quality flags:'+ '\n')
			datafile.writelines('[Bit 0]' + '    ' + 'Amplifier saturation detected (station dependent)' + '\n')
			datafile.writelines('[Bit 1]' + '    ' + 'Digitizer clipping detected' + '\n')
			datafile.writelines('[Bit 2]' + '    ' + 'Spikes detected' + '\n')
			datafile.writelines('[Bit 3]' + '    ' + 'Glitches detected' + '\n')
			datafile.writelines('[Bit 4]' + '    ' + 'Missing/padded data present' + '\n')
			datafile.writelines('[Bit 5]' + '    ' + 'Telemetry synchronization error' + '\n')
			datafile.writelines('[Bit 6]' + '    ' + 'A digital filter may be charging' + '\n')
			datafile.writelines('[Bit 7]' + '    ' + 'Time tag is questionable' + '\n')
			
			datafile.writelines('This will only work correctly if each record in the file has the same record length.' + '\n')
			'''
			datafile.writelines('----------------------------IRIS----------------------------'+ '\n')
			datafile.writelines('----------------------------DATAQ----------------------------'+ '\n')
			
			datafile.close()
		
		
		List_IRIS_BHE = []
		List_IRIS_BHN = []
		List_IRIS_BHZ = []
		
		
		for k in range(0, len_events):
			
			List_IRIS_BHE.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/BH_RAW/' + '*.BHE'))
			List_IRIS_BHN.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/BH_RAW/' + '*.BHN'))
			List_IRIS_BHZ.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/BH_RAW/' + '*.BHZ'))

			List_IRIS_BHE[k] = sorted(List_IRIS_BHE[k])
			List_IRIS_BHN[k] = sorted(List_IRIS_BHN[k])
			List_IRIS_BHZ[k] = sorted(List_IRIS_BHZ[k])

		
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHE
			
			gap_BHE = []
			Sta_BHE = []
			
			for i in range(0, len(List_IRIS_BHE[k])):
				st = read(List_IRIS_BHE[k][i])
				sta_BHE = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHE.append(sta_BHE)
				gap_BHE.append(st.getGaps())

			gap_prob_BHE = []

			for i in range(0, len(gap_BHE)):
				if gap_BHE[i] != []:
					gap_prob_BHE.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHE) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHE:
					gap_str = str(i) + '  ' + gap_BHE[i][0][0] + '  ' + gap_BHE[i][0][1] + '  ' + \
						gap_BHE[i][0][2] + '  ' + gap_BHE[i][0][3] + '  ' + str(len(gap_BHE[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHE = []
			TQ_BHE = []
			
			for i in range(0, len(List_IRIS_BHE[k])):
				
				try:
					
					TQ_BHE.append(mseed.getTimingQuality(List_IRIS_BHE[k][i]))
					DQ_BHE.append(mseed.getDataQualityFlagsCount(List_IRIS_BHE[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHE[i][0] +	'.' + Sta_BHE[i][1] + \
						'.' +Sta_BHE[i][2] + '.' + 'BHE'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/IRIS/Excep_py/' + 'excep_iris', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHE[i][0] + \
						'.' + Sta_BHE[i][1] + '.' + Sta_BHE[i][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHE = []
			
			for i in range(0, len(TQ_BHE)):
				if TQ_BHE[i] != {}:
					TQ_prob_BHE.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHE) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHE:
					time_str = str(i) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
						Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '  ' + str(TQ_BHE[i]['min']) + '  ' + str(TQ_BHE[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHE)):
				data_str = str(i) + '  ' + str(DQ_BHE[i]) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
					Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()


		
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHN
			
			gap_BHN = []
			Sta_BHN = []
			
			for i in range(0, len(List_IRIS_BHN[k])):
				st = read(List_IRIS_BHN[k][i])
				sta_BHN = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHN.append(sta_BHN)
				gap_BHN.append(st.getGaps())

			gap_prob_BHN = []

			for i in range(0, len(gap_BHN)):
				if gap_BHN[i] != []:
					gap_prob_BHN.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHN) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHN:
					gap_str = str(i) + '  ' + gap_BHN[i][0][0] + '  ' + gap_BHN[i][0][1] + '  ' + \
						gap_BHN[i][0][2] + '  ' + gap_BHN[i][0][3] + '  ' + str(len(gap_BHN[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHN = []
			TQ_BHN = []
			
			for i in range(0, len(List_IRIS_BHN[k])):
				
				try:
					
					TQ_BHN.append(mseed.getTimingQuality(List_IRIS_BHN[k][i]))
					DQ_BHN.append(mseed.getDataQualityFlagsCount(List_IRIS_BHN[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHN[i][0] +	'.' + Sta_BHN[i][1] + \
						'.' +Sta_BHN[i][2] + '.' + 'BHN'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/IRIS/Excep_py/' + 'excep_iris', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHN[i][0] + \
						'.' + Sta_BHN[i][1] + '.' + Sta_BHN[i][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHN = []
			
			for i in range(0, len(TQ_BHN)):
				if TQ_BHN[i] != {}:
					TQ_prob_BHN.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHN) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHN:
					time_str = str(i) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
						Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '  ' + str(TQ_BHN[i]['min']) + '  ' + str(TQ_BHN[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHN)):
				data_str = str(i) + '  ' + str(DQ_BHN[i]) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
					Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()
			
			
			
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHZ
			
			gap_BHZ = []
			Sta_BHZ = []
			
			for i in range(0, len(List_IRIS_BHZ[k])):
				st = read(List_IRIS_BHZ[k][i])
				sta_BHZ = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHZ.append(sta_BHZ)
				gap_BHZ.append(st.getGaps())

			gap_prob_BHZ = []

			for i in range(0, len(gap_BHZ)):
				if gap_BHZ[i] != []:
					gap_prob_BHZ.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHZ) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHZ:
					gap_str = str(i) + '  ' + gap_BHZ[i][0][0] + '  ' + gap_BHZ[i][0][1] + '  ' + \
						gap_BHZ[i][0][2] + '  ' + gap_BHZ[i][0][3] + '  ' + str(len(gap_BHZ[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHZ = []
			TQ_BHZ = []
			
			for i in range(0, len(List_IRIS_BHZ[k])):
				
				try:
					
					TQ_BHZ.append(mseed.getTimingQuality(List_IRIS_BHZ[k][i]))
					DQ_BHZ.append(mseed.getDataQualityFlagsCount(List_IRIS_BHZ[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHZ[i][0] +	'.' + Sta_BHZ[i][1] + \
						'.' +Sta_BHZ[i][2] + '.' + 'BHZ'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/IRIS/Excep_py/' + 'excep_iris', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHZ[i][0] + \
						'.' + Sta_BHZ[i][1] + '.' + Sta_BHZ[i][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHZ = []
			
			for i in range(0, len(TQ_BHZ)):
				if TQ_BHZ[i] != {}:
					TQ_prob_BHZ.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHZ) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHZ:
					time_str = str(i) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
						Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '  ' + str(TQ_BHZ[i]['min']) + '  ' + str(TQ_BHZ[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHZ)):
				data_str = str(i) + '  ' + str(DQ_BHZ[i]) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
					Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/IRIS/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()

###################################################### QC_ARC ######################################################

def QC_ARC(input):
	
	"""
	Quality Control (Gap, Timing Quality, Data Quality) for ArcLink stations.
	"""
	
	Address_data = input['Address']
	
	pre_ls_event = []
	
	tty = open(input['Address'] + '/tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				pre_ls_event.append(Address_data + '/' + tty_str[i][2])
	
	
	for i in range(0, len(pre_ls_event)):
		print 'Quality Check for: ' + '\n' + str(pre_ls_event[i])
	print '*************************************************************'
	
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
	
	add_ARC_QC = []
	
	for i in ls_event:
		add_ARC_QC.append(i + '/ARC/QC')
		
	add_ARC_events = []
	for i in pre_ls_event:
		add_ARC_events.append(i + '/EVENT/event_list')
		
	events_all = []
	
	for i in add_ARC_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	for l in range(0, len(events_all)):
		
		events = pickle.load(events_all[l])
		len_events = len(events)
		
		for k in range(0, len_events):
		
			if os.path.exists(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/QC/') == True:
				
				shutil.rmtree(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/QC/')
				os.makedirs(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/QC/')
				
			else:
				os.makedirs(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/QC/')	

		for k in range(0, len_events):
		
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'GAP', 'w')
			eventsID = events[k]['event_id']
			gapfile.writelines('\n' + eventsID + '\n')
			gapfile.writelines('----------------------------ARC----------------------------'+ '\n')
			gapfile.writelines('----------------------------GAP----------------------------'+ '\n')
			gapfile.close()
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'TimingQuality', 'w')
			eventsID = events[k]['event_id']
			timefile.writelines('\n' + eventsID + '\n')
			'''
			timefile.writelines('\n' + '----------------------------------' + '\n')
			timefile.writelines('Description:' + '\n')
			timefile.writelines('timing quality in percent (0-100).' + '\n')
			timefile.writelines('0: the timing is completely unreliable' + '\n')
			'''
			timefile.writelines('----------------------------ARC----------------------------'+ '\n')
			timefile.writelines('----------------------------TIMEQ----------------------------'+ '\n')
			timefile.close()
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'DataQuality', 'w')
			eventsID = events[k]['event_id']
			datafile.writelines('\n' + eventsID + '\n')
			'''
			datafile.writelines('\n' + '----------------------------------' + '\n')
			datafile.writelines('Description:' + '\n')
			datafile.writelines('Counts all data quality flags of the given MiniSEED file. This method will count all set data quality' + '\n' + 
				'flag bits in the fixed section of the data header in a MiniSEED file and returns the total count for each flag type.' + '\n' + 'Data quality flags:'+ '\n')
			datafile.writelines('[Bit 0]' + '    ' + 'Amplifier saturation detected (station dependent)' + '\n')
			datafile.writelines('[Bit 1]' + '    ' + 'Digitizer clipping detected' + '\n')
			datafile.writelines('[Bit 2]' + '    ' + 'Spikes detected' + '\n')
			datafile.writelines('[Bit 3]' + '    ' + 'Glitches detected' + '\n')
			datafile.writelines('[Bit 4]' + '    ' + 'Missing/padded data present' + '\n')
			datafile.writelines('[Bit 5]' + '    ' + 'Telemetry synchronization error' + '\n')
			datafile.writelines('[Bit 6]' + '    ' + 'A digital filter may be charging' + '\n')
			datafile.writelines('[Bit 7]' + '    ' + 'Time tag is questionable' + '\n')
			
			datafile.writelines('This will only work correctly if each record in the file has the same record length.' + '\n')
			'''
			datafile.writelines('----------------------------ARC----------------------------'+ '\n')
			datafile.writelines('----------------------------DATAQ----------------------------'+ '\n')
			
			datafile.close()
		
		
		List_ARC_BHE = []
		List_ARC_BHN = []
		List_ARC_BHZ = []
		
		
		for k in range(0, len_events):
			
			List_ARC_BHE.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/BH_RAW/' + '*.BHE'))
			List_ARC_BHN.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/BH_RAW/' + '*.BHN'))
			List_ARC_BHZ.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/ARC/BH_RAW/' + '*.BHZ'))

			List_ARC_BHE[k] = sorted(List_ARC_BHE[k])
			List_ARC_BHN[k] = sorted(List_ARC_BHN[k])
			List_ARC_BHZ[k] = sorted(List_ARC_BHZ[k])

		
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHE
			
			gap_BHE = []
			Sta_BHE = []
			
			for i in range(0, len(List_ARC_BHE[k])):
				st = read(List_ARC_BHE[k][i])
				sta_BHE = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHE.append(sta_BHE)
				gap_BHE.append(st.getGaps())

			gap_prob_BHE = []

			for i in range(0, len(gap_BHE)):
				if gap_BHE[i] != []:
					gap_prob_BHE.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHE) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHE:
					gap_str = str(i) + '  ' + gap_BHE[i][0][0] + '  ' + gap_BHE[i][0][1] + '  ' + \
						gap_BHE[i][0][2] + '  ' + gap_BHE[i][0][3] + '  ' + str(len(gap_BHE[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHE = []
			TQ_BHE = []
			
			for i in range(0, len(List_ARC_BHE[k])):
				
				try:
					
					TQ_BHE.append(mseed.getTimingQuality(List_ARC_BHE[k][i]))
					DQ_BHE.append(mseed.getDataQualityFlagsCount(List_ARC_BHE[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHE[i][0] +	'.' + Sta_BHE[i][1] + \
						'.' +Sta_BHE[i][2] + '.' + 'BHE'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHE[i][0] + \
						'.' + Sta_BHE[i][1] + '.' + Sta_BHE[i][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHE = []
			
			for i in range(0, len(TQ_BHE)):
				if TQ_BHE[i] != {}:
					TQ_prob_BHE.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHE) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHE:
					time_str = str(i) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
						Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '  ' + str(TQ_BHE[i]['min']) + '  ' + str(TQ_BHE[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHE)):
				data_str = str(i) + '  ' + str(DQ_BHE[i]) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
					Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()


		
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHN
			
			gap_BHN = []
			Sta_BHN = []
			
			for i in range(0, len(List_ARC_BHN[k])):
				st = read(List_ARC_BHN[k][i])
				sta_BHN = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHN.append(sta_BHN)
				gap_BHN.append(st.getGaps())

			gap_prob_BHN = []

			for i in range(0, len(gap_BHN)):
				if gap_BHN[i] != []:
					gap_prob_BHN.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHN) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHN:
					gap_str = str(i) + '  ' + gap_BHN[i][0][0] + '  ' + gap_BHN[i][0][1] + '  ' + \
						gap_BHN[i][0][2] + '  ' + gap_BHN[i][0][3] + '  ' + str(len(gap_BHN[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHN = []
			TQ_BHN = []
			
			for i in range(0, len(List_ARC_BHN[k])):
				
				try:
					
					TQ_BHN.append(mseed.getTimingQuality(List_ARC_BHN[k][i]))
					DQ_BHN.append(mseed.getDataQualityFlagsCount(List_ARC_BHN[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHN[i][0] +	'.' + Sta_BHN[i][1] + \
						'.' +Sta_BHN[i][2] + '.' + 'BHN'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHN[i][0] + \
						'.' + Sta_BHN[i][1] + '.' + Sta_BHN[i][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHN = []
			
			for i in range(0, len(TQ_BHN)):
				if TQ_BHN[i] != {}:
					TQ_prob_BHN.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHN) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHN:
					time_str = str(i) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
						Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '  ' + str(TQ_BHN[i]['min']) + '  ' + str(TQ_BHN[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHN)):
				data_str = str(i) + '  ' + str(DQ_BHN[i]) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
					Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()
			
			
			
		#-------------------------------get-GAP--------------------------------
		
		#-------------------------------BHZ
			
			gap_BHZ = []
			Sta_BHZ = []
			
			for i in range(0, len(List_ARC_BHZ[k])):
				st = read(List_ARC_BHZ[k][i])
				sta_BHZ = [st[0].stats['network'], st[0].stats['station'], st[0].stats['location'], st[0].stats['channel']]
				Sta_BHZ.append(sta_BHZ)
				gap_BHZ.append(st.getGaps())

			gap_prob_BHZ = []

			for i in range(0, len(gap_BHZ)):
				if gap_BHZ[i] != []:
					gap_prob_BHZ.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)
			
			GAP_str = []
			
			if len(gap_prob_BHZ) == 0:
				GAP_str.append('None')
			
			else:
				for i in gap_prob_BHZ:
					gap_str = str(i) + '  ' + gap_BHZ[i][0][0] + '  ' + gap_BHZ[i][0][1] + '  ' + \
						gap_BHZ[i][0][2] + '  ' + gap_BHZ[i][0][3] + '  ' + str(len(gap_BHZ[i])) + '\n'
					GAP_str.append(gap_str)
				
			
			gapfile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'GAP', 'a')
			gapfile.writelines(GAP_str)
			gapfile.writelines('\n')
			gapfile.close()
			
			
			#-------------------------------Timing-Quality and Data-Quality--------------------------------
			
			mseed = LibMSEED()

			DQ_BHZ = []
			TQ_BHZ = []
			
			for i in range(0, len(List_ARC_BHZ[k])):
				
				try:
					
					TQ_BHZ.append(mseed.getTimingQuality(List_ARC_BHZ[k][i]))
					DQ_BHZ.append(mseed.getDataQualityFlagsCount(List_ARC_BHZ[k][i]))				
			
				except Exception, e:	
						
					print 'TQ-DQ' + '---' + Sta_BHZ[i][0] +	'.' + Sta_BHZ[i][1] + \
						'.' +Sta_BHZ[i][2] + '.' + 'BHZ'
						
					Exception_file = open(pre_ls_event[l] + '/' + \
						events[k]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = 'TQ-DQ' + '---' + str(l) + '-' + str(k) + '-' + str(i) + '---' + Sta_BHZ[i][0] + \
						'.' + Sta_BHZ[i][1] + '.' + Sta_BHZ[i][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHZ = []
			
			for i in range(0, len(TQ_BHZ)):
				if TQ_BHZ[i] != {}:
					TQ_prob_BHZ.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all)) + ' -- ' + str(k+1) + '/' + str(len_events)

			
			TIME_str = []
			
			if len(TQ_prob_BHZ) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHZ:
					time_str = str(i) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
						Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '  ' + str(TQ_BHZ[i]['min']) + '  ' + str(TQ_BHZ[i]['max']) + '\n'
					TIME_str.append(time_str)
				
			
			timefile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'TimingQuality', 'a')
			timefile.writelines(TIME_str)
			timefile.writelines('\n')
			timefile.close()			
			
			
			DATA_str = []
			
			for i in range(0, len(DQ_BHZ)):
				data_str = str(i) + '  ' + str(DQ_BHZ[i]) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
					Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '\n'
				DATA_str.append(data_str)
			
			
			datafile = open(pre_ls_event[l] + '/' + events[k]['event_id'] + \
					'/ARC/QC/' + 'DataQuality', 'a')
			datafile.writelines(DATA_str)
			datafile.writelines('\n')
			datafile.close()



if __name__ == "__main__":
	status = ObsPyDMT()
	sys.exit(status)
