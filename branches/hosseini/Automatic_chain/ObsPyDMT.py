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
		
		if input['mass'] == 'Y':
			
			print '\n' + '************************************************************************************************'
			print 'ArcLink -- Download all waveforms, Response file and other information based on requested events'
			print '************************************************************************************************'
					
			(Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink) = \
				Arclink_get_Network(input)
		
			Arclink_get_Waveform(input, Nets_Arc_req_BHE, \
				Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t_arclink)

		else:
			
			print '\n' + '**************************************************************************************************'
			print 'ArcLink -- Download single waveform, Response file and other information based on requested events'
			print '**************************************************************************************************'
			
			Arclink_get_Waveform_single(input)
				
	# ------------------------Updating--------------------------------
	if input['update_iris'] == 'Y':
		
		print '\n' + '*********************'
		print 'IRIS -- Updating Mode' + '\n'
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
		channel = 'BHE'
		IRIS_get_Waveform(input, Stas_iris, t, channel)
	
	if input['BHN'] == 'Y':
		channel = 'BHN'
		IRIS_get_Waveform(input, Stas_iris, t, channel)
	
	if input['BHZ'] == 'Y':
		channel = 'BHZ'
		IRIS_get_Waveform(input, Stas_iris, t, channel)

	print "-------------------------------------------------"
	print 'IRIS is DONE'
	print "-------------------------------------------------"

###################################################### IRIS_get_Waveform ######################################################

def IRIS_get_Waveform(input, Stas_iris, t, channel):
	
	t_wave_1 = datetime.now()
	
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
		
		
	for i in range(0, len_events):
		print "--------------------"
		if input['TEST'] == 'Y':
			len_req_iris = input['TEST_no']

		else:	
			len_req_iris = len(Sta_req[i])

		dic = {}				
			
		for j in range(0, len_req_iris):
		
			print '------------------'
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
	
	Station_file = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/info/' + 'avail_iris_' + channel, 'a')
	pickle.dump(dic, Station_file)
	Station_file.close()
			
	Report = open(Address_events + '/' + events[i]['event_id'] + '/IRIS/info/' + 'report_st', 'a')
	eventsID = events[i]['event_id']
	Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
	Report.writelines(eventsID + '\n')
	Report.writelines('---------------IRIS---------------' + '\n')
	Report.writelines('---------------' + channel + '---------------' + '\n')
	rep = 'IRIS-Available stations for channel ' + channel + ' and for event' + '-' + str(i) + ': ' + str(len(Sta_req[i])) + '\n'
	Report.writelines(rep)
	rep = 'IRIS-Saved stations for channel ' + channel + ' and for event' + '-' + str(i) + ':     ' + str(len(dic)) + '\n'
	Report.writelines(rep)
	Report.writelines('----------------------------------' + '\n')
	
	t_wave_2 = datetime.now()
	t_wave = t_wave_2 - t_wave_1
	
	rep = "Time for getting and saving Waveforms from IRIS: " + str(t_wave) + '\n'
	Report.writelines(rep)
	Report.writelines('----------------------------------' + '\n')
	Report.close()

###################################################### Arclink_get_Network ######################################################

def Arclink_get_Network(input):
	
	"""
	Arclink: Returns available stations for all requested events
	-----------------
	Problems:
	- ['BW', 'WETR', '', 'BH*']
	- Client_arclink(command_delay=0.1)
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
	
	Networks_Arclink = []
	Nets_Arc_req_BHE = []
	Nets_Arc_req_BHN = []
	Nets_Arc_req_BHZ = []

	for i in range(0, len_events):
		
		t.append(UTCDateTime(events[i]['datetime']))
	
		try:
			
			Networks_Arclink.append(client_arclink.getNetworks(t[i]-10, t[i]+10))
			print 'ArcLink-Availability for event: ' + str(i) + '  --->' + 'DONE'

		except Exception, e:
				
			Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/Excep_py/' + 'excep_avail', 'a')
			ee = 'Event:' + str(i) + '---' + str(e) + '\n'
			
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
				
		nets_Arc_req_BHE=sorted([X for X in Networks_Arclink[i].keys() if ".BHE" in X])
		Nets_Arc_req_BHE.append(nets_Arc_req_BHE)	
		nets_Arc_req_BHN=sorted([X for X in Networks_Arclink[i].keys() if ".BHN" in X])
		Nets_Arc_req_BHN.append(nets_Arc_req_BHN)
		nets_Arc_req_BHZ=sorted([X for X in Networks_Arclink[i].keys() if ".BHZ" in X])
		Nets_Arc_req_BHZ.append(nets_Arc_req_BHZ)

	
		
	#client_arclink.close()
	
	for i in range(0, len_events):
		len_req_Arc_BHE = len(Nets_Arc_req_BHE[i])
		for j in range(0, len_req_Arc_BHE):
			Nets_Arc_req_BHE[i][j] = Nets_Arc_req_BHE[i][j].split('.')

	for i in range(0, len_events):
		len_req_Arc_BHN = len(Nets_Arc_req_BHN[i])
		for j in range(0, len_req_Arc_BHN):
			Nets_Arc_req_BHN[i][j] = Nets_Arc_req_BHN[i][j].split('.')

	for i in range(0, len_events):
		len_req_Arc_BHZ = len(Nets_Arc_req_BHZ[i])
		for j in range(0, len_req_Arc_BHZ):
			Nets_Arc_req_BHZ[i][j] = Nets_Arc_req_BHZ[i][j].split('.')
	
	for j in range(0, len_events):
		for i in range(0, len(Nets_Arc_req_BHE[j])):
			if Nets_Arc_req_BHE[j][i] == ['BW', 'WETR', '', 'BHE']:
				del Nets_Arc_req_BHE[j][i]
				break
		
		for i in range(0, len(Nets_Arc_req_BHN[j])):
			if Nets_Arc_req_BHN[j][i] == ['BW', 'WETR', '', 'BHN']:
				del Nets_Arc_req_BHN[j][i]
				break
		
		for i in range(0, len(Nets_Arc_req_BHZ[j])):
			if Nets_Arc_req_BHZ[j][i] == ['BW', 'WETR', '', 'BHZ']:
				del Nets_Arc_req_BHZ[j][i]
				break
	
	
	for i in range(0, len_events):
		print "--------------------"
		print 'ARC-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHE)
		print 'ARC-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHN)
		print 'ARC-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHZ)
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		eventsID = events[i]['event_id']
		Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
		Report.writelines(eventsID + '\n')		
		Report.writelines('---------------ArcLink---------------' + '\n')
		rep1 = 'ARC-Available stations (BHE) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHE) + '\n'
		rep2 = 'ARC-Available stations (BHN) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHN) + '\n'
		rep3 = 'ARC-Available stations (BHZ) for event' + '-' + str(i) + ':' + str(len_req_Arc_BHZ) + '\n'
		Report.writelines(rep1)
		Report.writelines(rep2)
		Report.writelines(rep3)
		Report.writelines('----------------------------------' + '\n')
		Report.close()
		
	for i in range(0, len_events):
		Station_file1 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'All_ARC_Stations_BHE', 'w')
		pickle.dump(Nets_Arc_req_BHE[i], Station_file1)
		Station_file1.close()
		
		Station_file2 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'All_ARC_Stations_BHN', 'w')
		pickle.dump(Nets_Arc_req_BHN[i], Station_file2)
		Station_file2.close()
		
		Station_file3 = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'All_ARC_Stations_BHZ', 'w')
		pickle.dump(Nets_Arc_req_BHZ[i], Station_file3)
		Station_file3.close()
		
	t_arc_2 = datetime.now()
	t_arc_21 = t_arc_2 - t_arc_1
	
	print "--------------------"
	print 'ARC-Time: (Availability)'
	print t_arc_21
	
	return Nets_Arc_req_BHE, Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t

###################################################### Arclink_get_Waveform ######################################################

def Arclink_get_Waveform(input, Nets_Arc_req_BHE, \
	Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t):
	
	"""
	Gets Waveforms, Response files and other information from ArcLink based on the requested events...
	-----------------
	Problems:
	- Client_arclink(command_delay=0.1)
	"""
	
	t_wave_1 = datetime.now()
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/Excep_py/' + 'Exception_file_ARC', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'Avail_ARC_Stations_BHE', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'Avail_ARC_Stations_BHN', 'w')
		Station_file.close()
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'Avail_ARC_Stations_BHZ', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'iris_BHE', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'iris_BHN', 'w')
		Syn_file.close()
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'iris_BHZ', 'w')
		Syn_file.close()
	
	for i in range(0, len_events):
		
		t_wave_1 = datetime.now()
		
		if input['TEST'] == 'Y':
			len_req_Arc_BHE = input['TEST_no']
			len_req_Arc_BHN = input['TEST_no']
			len_req_Arc_BHZ = input['TEST_no']

		else:	
			len_req_Arc_BHE = len(Nets_Arc_req_BHE[i]) 
			len_req_Arc_BHN = len(Nets_Arc_req_BHN[i]) 
			len_req_Arc_BHZ = len(Nets_Arc_req_BHZ[i]) 		
		
		
		inv_BHE = {}
		
		if input['BHE'] == 'Y':
			
			for j in range(0, len_req_Arc_BHE):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i) + '-' + str(j) + '-BHE'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHE
					if input['waveform'] == 'Y':
						
						dummy = 'Waveform'
						
						client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
							Nets_Arc_req_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
						
						print "Saving Waveform for: " + Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"  
					
					if input['response'] == 'Y':

						dummy = 'Response'
						
						client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
							Nets_Arc_req_BHE[i][j][2], 'BHE', t[i]-input['t_before'], t[i]+input['t_after'])
						
						sp = Parser(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')
						
						sp.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp')
							
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')	
						'''	
					
						print "Saving Response for: " + Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
							Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
						
					
					dummy = 'Inventory'
					
					inv_BHE[j] = client_arclink.getInventory(Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
						Nets_Arc_req_BHE[i][j][2], 'BHE')
					
					dum = Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1]
					
					if input['SAC'] == 'Y':
									
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
								Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
								Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', 'SAC')
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
								Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE')
						
						if inv_BHE[j][dum]['latitude'] != None:
							st[0].stats['sac']['stla'] = inv_BHE[j][dum]['latitude']
						if inv_BHE[j][dum]['longitude'] != None:
							st[0].stats['sac']['stlo'] = inv_BHE[j][dum]['longitude']
						if inv_BHE[j][dum]['elevation'] != None:
							st[0].stats['sac']['stel'] = inv_BHE[j][dum]['elevation']
						if inv_BHE[j][dum]['depth'] != None:
							st[0].stats['sac']['stdp'] = inv_BHE[j][dum]['depth']
						
						st[0].stats['sac']['evla'] = events[i]['latitude']
						st[0].stats['sac']['evlo'] = events[i]['longitude']
						st[0].stats['sac']['evdp'] = events[i]['depth']
						st[0].stats['sac']['mag'] = events[i]['magnitude']
						
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
								Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE', 'SAC')

					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/info/' + 'iris_BHE', 'a')
					syn = Nets_Arc_req_BHE[i][j][0] + ',' + Nets_Arc_req_BHE[i][j][1] + ',' + \
						Nets_Arc_req_BHE[i][j][2] + ',' + Nets_Arc_req_BHE[i][j][3] + ',' + str(inv_BHE[j][dum]['latitude']) + \
						',' + str(inv_BHE[j][dum]['longitude']) + ',' + str(inv_BHE[j][dum]['elevation']) + ',' + \
						str(inv_BHE[j][dum]['depth']) + ',' + events[i]['event_id'] + ',' + str(events[i]['latitude']) \
						 + ',' + str(events[i]['longitude']) + ',' + str(events[i]['depth']) + ',' + str(events[i]['magnitude']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHE[i][j][0] +	'.' + Nets_Arc_req_BHE[i][j][1] + \
						'.' +Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHE[i][j][0] + \
						'.' + Nets_Arc_req_BHE[i][j][1] + '.' + \
						Nets_Arc_req_BHE[i][j][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'Avail_ARC_Stations_BHE', 'a')
		pickle.dump(inv_BHE, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		
		
		
		inv_BHN = {}
		
		if input['BHN'] == 'Y':
			
			for j in range(0, len_req_Arc_BHN):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i) + '-' + str(j) + '-BHN'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHN
					if input['waveform'] == 'Y':
						
						dummy = 'Waveform'
						
						client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
							Nets_Arc_req_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
						
						print "Saving Waveform for: " + Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"  
					
					
					if input['response'] == 'Y':
							
						dummy = 'Response'
						
						client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
							Nets_Arc_req_BHN[i][j][2], 'BHN', t[i]-input['t_before'], t[i]+input['t_after'])
						
						sp = Parser(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
						
						sp.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp')
						
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
						'''
					
										
						print "Saving Response for: " + Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
							Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
						
					
					dummy = 'Inventory'
					
					inv_BHN[j] = client_arclink.getInventory(Nets_Arc_req_BHN[i][j][0], Nets_Arc_req_BHN[i][j][1], \
						Nets_Arc_req_BHN[i][j][2], 'BHN')
					
					dum = Nets_Arc_req_BHN[i][j][0] + '.' + Nets_Arc_req_BHN[i][j][1]
					
					if input['SAC'] == 'Y':
									
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
								Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
								Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', 'SAC')
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
								Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
								
						if inv_BHN[j][dum]['latitude'] != None:
							st[0].stats['sac']['stla'] = inv_BHN[j][dum]['latitude']
						if inv_BHN[j][dum]['longitude'] != None:
							st[0].stats['sac']['stlo'] = inv_BHN[j][dum]['longitude']
						if inv_BHN[j][dum]['elevation'] != None:
							st[0].stats['sac']['stel'] = inv_BHN[j][dum]['elevation']
						if inv_BHN[j][dum]['depth'] != None:
							st[0].stats['sac']['stdp'] = inv_BHN[j][dum]['depth']
						
						st[0].stats['sac']['evla'] = events[i]['latitude']
						st[0].stats['sac']['evlo'] = events[i]['longitude']
						st[0].stats['sac']['evdp'] = events[i]['depth']
						st[0].stats['sac']['mag'] = events[i]['magnitude']
						
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
								Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN', 'SAC')

					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/info/' + 'iris_BHN', 'a')
					syn = Nets_Arc_req_BHN[i][j][0] + ',' + Nets_Arc_req_BHN[i][j][1] + ',' + \
						Nets_Arc_req_BHN[i][j][2] + ',' + Nets_Arc_req_BHN[i][j][3] + ',' + str(inv_BHN[j][dum]['latitude']) + \
						',' + str(inv_BHN[j][dum]['longitude']) + ',' + str(inv_BHN[j][dum]['elevation']) + ',' + \
						str(inv_BHN[j][dum]['depth']) + ',' + events[i]['event_id'] + ',' + str(events[i]['latitude']) \
						 + ',' + str(events[i]['longitude']) + ',' + str(events[i]['depth']) + ',' + str(events[i]['magnitude']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + \
						'.' +Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHN[i][j][0] + \
						'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
						Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'Avail_ARC_Stations_BHN', 'a')
		pickle.dump(inv_BHN, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHN) for event' + '-' + str(i) + ': ' + str(len(inv_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()	
		

		inv_BHZ = {}
		
		if input['BHZ'] == 'Y':
			
			for j in range(0, len_req_Arc_BHZ):
			
				print '------------------'
				print 'ArcLink-Event and Station Numbers are:'
				print str(i) + '-' + str(j) + '-BHZ'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHZ
					if input['waveform'] == 'Y':
							
						dummy = 'Waveform'
						
						client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/BH_RAW/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
							Nets_Arc_req_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
						
						print "Saving Waveform for: " + Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"  
						
					
					if input['response'] == 'Y':
							
						dummy = 'Response'
						
						client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
							Nets_Arc_req_BHZ[i][j][2], 'BHZ', t[i]-input['t_before'], t[i]+input['t_after'])
						
						sp = Parser(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
						
						sp.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp')
						
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
						'''
					
						print "Saving Response for: " + Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
							Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
							
					
					
					dummy = 'Inventory'
					
					inv_BHZ[j] = client_arclink.getInventory(Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
						Nets_Arc_req_BHZ[i][j][2], 'BHZ')
					
					dum = Nets_Arc_req_BHZ[i][j][0] + '.' + Nets_Arc_req_BHZ[i][j][1]
					
					if input['SAC'] == 'Y':
								
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
								Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
								Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', 'SAC')
						st = read(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
								Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
						
						if inv_BHZ[j][dum]['latitude'] != None:
							st[0].stats['sac']['stla'] = inv_BHZ[j][dum]['latitude']
						if inv_BHZ[j][dum]['longitude'] != None:
							st[0].stats['sac']['stlo'] = inv_BHZ[j][dum]['longitude']
						if inv_BHZ[j][dum]['elevation'] != None:
							st[0].stats['sac']['stel'] = inv_BHZ[j][dum]['elevation']
						if inv_BHZ[j][dum]['depth'] != None:
							st[0].stats['sac']['stdp'] = inv_BHZ[j][dum]['depth']
						
						st[0].stats['sac']['evla'] = events[i]['latitude']
						st[0].stats['sac']['evlo'] = events[i]['longitude']
						st[0].stats['sac']['evdp'] = events[i]['depth']
						st[0].stats['sac']['mag'] = events[i]['magnitude']
						
						st[0].write(Address_events + '/' + events[i]['event_id'] + \
								'/ARC/BH_RAW/' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
								Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ', 'SAC')

					Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
						'/ARC/info/' + 'iris_BHZ', 'a')
					syn = Nets_Arc_req_BHZ[i][j][0] + ',' + Nets_Arc_req_BHZ[i][j][1] + ',' + \
						Nets_Arc_req_BHZ[i][j][2] + ',' + Nets_Arc_req_BHZ[i][j][3] + ',' + str(inv_BHZ[j][dum]['latitude']) + \
						',' + str(inv_BHZ[j][dum]['longitude']) + ',' + str(inv_BHZ[j][dum]['elevation']) + ',' + \
						str(inv_BHZ[j][dum]['depth']) + ',' + events[i]['event_id'] + ',' + str(events[i]['latitude']) \
						 + ',' + str(events[i]['longitude']) + ',' + str(events[i]['depth']) + ',' + str(events[i]['magnitude']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "Saving Station  for: " + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + \
						'.' +Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ'
					
					Exception_file = open(Address_events + '/' + \
						events[i]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

					ee = dummy + '---' + str(i) + '-' + str(j) + '---' + Nets_Arc_req_BHZ[i][j][0] + \
						'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
						Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'Avail_ARC_Stations_BHZ', 'a')
		pickle.dump(inv_BHZ, Station_file)
		Station_file.close()
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHZ) for event' + '-' + str(i) + ': ' + str(len(inv_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	
	
	
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		Report.writelines('----------------------------------' + '\n')
		rep1 = "Time for getting and saving Waveforms from ArcLink: " + str(t_wave) + '\n'
		Report.writelines(rep1)
		Report.writelines('----------------------------------' + '\n' + '\n')
		Report.close()
		
		print "-------------------------------------------------"
		print 'ArcLink is DONE'
		print "Time for getting and saving Waveforms from ArcLink:"
		print t_wave

###################################################### Arclink_get_Waveform_single ######################################################

def Arclink_get_Waveform_single(input):
	
	"""
	Gets one Waveform, Response file and other information from ArcLink based on the requested network, station, location, channel and events...
	ATTENTION: In this case, you should exactly know the net, sta, loc, cha of your request. Wild-cards are not allowed!
	-----------------
	Problems:
	- Client_arclink(command_delay=0.1)
	"""
	
	t_wave_1 = datetime.now()
	
	Networks_ARC = [input['net'], input['sta'], input['loc'], input['cha']]
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/' + Period
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
		
	t = []
	for i in range(0, len_events):
		t.append(UTCDateTime(events[i]['datetime']))
	
	for i in range(0, len_events):
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/Resp/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/info/')
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/ARC/Excep_py/')
		
	for i in range(0, len_events):
		Exception_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/Excep_py/' + 'Exception_file_ARC', 'w')
		eventsID = events[i]['event_id']
		Exception_file.writelines('\n' + eventsID + '\n')
		Exception_file.writelines('----------------------------ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		Exception_file.close()
		
		Station_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'Avail_ARC_Stations', 'w')
		Station_file.close()
		
		Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
			'/ARC/info/' + 'Input_Syn', 'w')
		Syn_file.close()
	
	
	client_arclink = Client_arclink(timeout=5)
	
	for i in range(0, len_events):
		
		print '------------------'
		print 'ArcLink-Event Number is:'
		print str(i)
		
		inv = {}
				
		try:
				
			client_arclink = Client_arclink(timeout=5)
					
			if input['waveform'] == 'Y':
					
				dummy = 'Waveform'
					
				client_arclink.saveWaveform(Address_events + '/' + events[i]['event_id'] + \
					'/ARC/BH_RAW/' + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
					Networks_ARC[2] + '.' + Networks_ARC[3], Networks_ARC[0], Networks_ARC[1], \
					Networks_ARC[2], Networks_ARC[3], t[i]-input['t_before'], t[i]+input['t_after'])
						
				print "Saving Waveform for: " + Networks_ARC[0] + '.' + Networks_ARC[1] + '.' + \
					Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"  
					
			if input['response'] == 'Y':
									
				dummy = 'Response'
						
				client_arclink.saveResponse(Address_events + '/' + events[i]['event_id'] + \
					'/ARC/Resp/' + 'RESP' + '.' + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
					Networks_ARC[2] + '.' + Networks_ARC[3], Networks_ARC[0], Networks_ARC[1], \
					Networks_ARC[2], Networks_ARC[3], t[i]-input['t_before'], t[i]+input['t_after'])
											
				print "Saving Response for: " + Networks_ARC[0] + '.' + Networks_ARC[1] + '.' + \
					Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"
							
					
			dummy = 'Inventory'
					
			inv = client_arclink.getInventory(Networks_ARC[0], Networks_ARC[1], \
				Networks_ARC[2], Networks_ARC[3])
										
			print "Saving Station  for: " + Networks_ARC[0] +	'.' + Networks_ARC[1] + '.' + \
				Networks_ARC[2] + '.' + Networks_ARC[3] + "  ---> DONE"
				
		except Exception, e:	
					
			print dummy + '---' + Networks_ARC[0] +	'.' + Networks_ARC[1] + \
				'.' +Networks_ARC[2] + '.' + Networks_ARC[3]
					
			Exception_file = open(Address_events + '/' + \
				events[i]['event_id'] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'a')

			ee = dummy + '---' + str(i) + '---' + Networks_ARC[0] + \
				'.' + Networks_ARC[1] + '.' + Networks_ARC[2] + '.' + Networks_ARC[3] + \
				'---' + str(e) + '\n'
					
			Exception_file.writelines(ee)
			Exception_file.close()
			print e
		
		
		#client_arclink.close()
		
		if len(inv) == 0:
			print 'No waveform Available'
		
		else:
			
			Station_file = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'Avail_ARC_Stations_BHE', 'a')
			pickle.dump(inv, Station_file)
			Station_file.close()
			
			
			Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
			rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv)) + '\n'
			Report.writelines(rep1)
			Report.close()	
			
			dum = Networks_ARC[0] + '.' + Networks_ARC[1]
			Syn_file = open(Address_events + '/' + events[i]['event_id'] + \
				'/ARC/info/' + 'Input_Syn', 'a')
			
			syn = Networks_ARC[0] + '  ' + Networks_ARC[1] + '  ' + \
				Networks_ARC[2] + '  ' + Networks_ARC[3] + '  ' + str(inv[dum]['latitude']) + \
				'  ' + str(inv[dum]['longitude']) + '  ' + str(inv[dum]['elevation']) + '  ' + \
				str(inv[dum]['depth']) + '\n'
			
			Syn_file.writelines(syn)
			Syn_file.close()		
		
		t_wave_2 = datetime.now()
		t_wave = t_wave_2 - t_wave_1
		
		
		Report = open(Address_events + '/' + events[i]['event_id'] + '/ARC/info/' + 'report_st', 'a')
		Report.writelines('----------------------------------' + '\n')
		rep1 = "Time for getting and saving Waveforms from ArcLink: " + str(t_wave) + '\n'
		Report.writelines(rep1)
		Report.writelines('----------------------------------' + '\n' + '\n')
		Report.close()
		
	print "-------------------------------------------------"
	print 'ArcLink is DONE'
	print "Time for getting and saving Waveforms from ArcLink:"
	print t_wave

###################################################### get_address ######################################################
'''
def get_address(interactive = input['inter_address']):
	
	"""
	This program gets the address required for next steps of the program
	"""
	
	if interactive == 'Y':
		print '----------------------------------------------------'
		address = raw_input('Please enter the target address:' + '\n')
		print '----------------------------------------------------'
		
	else:
		print '----------------------------------------------------'
		print 'The process is about to start...'
		print '----------------------------------------------------'
	
	return address
'''
###################################################### update_IRIS ######################################################

def update_IRIS(input):
	
	"""
	Updating the station folders from IRIS web-service
	Attention: This module update all station folders for all events in one directory.
	-----------------
	Problems:
	- excep_iris_update OR excep_iris?
	"""
	
	t_update_1 = datetime.now()
	
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
		add_IRIS_events.append(i + '/EVENT/event_list')
		
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

		ls_stas_open = open(ls_event[l] + '/IRIS/info/all_iris_BHE', 'r')
		all_iris_BHE = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/info/all_iris_BHN', 'r')
		all_iris_BHN = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/IRIS/info/all_iris_BHZ', 'r')
		all_iris_BHZ = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		for i in range(0, len(all_iris_BHE)):
			all_iris_BHE[i] = [all_iris_BHE[i][0], all_iris_BHE[i][1], \
				all_iris_BHE[i][2], all_iris_BHE[i][3]]
				
		for i in range(0, len(all_iris_BHN)):
			all_iris_BHN[i] = [all_iris_BHN[i][0], all_iris_BHN[i][1], \
				all_iris_BHN[i][2], all_iris_BHN[i][3]]
		
		for i in range(0, len(all_iris_BHZ)):
			all_iris_BHZ[i] = [all_iris_BHZ[i][0], all_iris_BHZ[i][1], \
				all_iris_BHZ[i][2], all_iris_BHZ[i][3]]
			
		'''
		upfile = open(ls_event[l] + '/IRIS/info/' + 'UPDATE', 'w')
		upfile.writelines('\n' + ls_event[l].split('/')[-1] + '\n')
		upfile.writelines('----------------------------IRIS----------------------------'+ '\n')
		upfile.writelines('----------------------------UPDATED----------------------------'+ '\n')
		upfile.close()
		'''		
		
		pre_Sta_BHE = []
		pre_Sta_BHN = []
		pre_Sta_BHZ = []
		
		Sta_BHE = []
		Sta_BHN = []
		Sta_BHZ = []
		
		
		file_BHE = open(ls_event[l] + '/IRIS/info/iris_BHE', 'r')
		
		pre_Sta_BHE = file_BHE.readlines()
		
		for i in range(0, len(pre_Sta_BHE)):
			pre_Sta_BHE[i] = pre_Sta_BHE[i].split(',')
		
		for i in range(0, len(pre_Sta_BHE)):
			if pre_Sta_BHE[i][2] == '  ':
				pre_Sta_BHE[i][2] = ''
			pre_Sta_BHE[i] = [pre_Sta_BHE[i][0], pre_Sta_BHE[i][1], pre_Sta_BHE[i][2], pre_Sta_BHE[i][3]]
			Sta_BHE.append(pre_Sta_BHE[i])
		
		
		file_BHN = open(ls_event[l] + '/IRIS/info/iris_BHN', 'r')
		
		pre_Sta_BHN = file_BHN.readlines()
		
		for i in range(0, len(pre_Sta_BHN)):
			pre_Sta_BHN[i] = pre_Sta_BHN[i].split(',')
		
		for i in range(0, len(pre_Sta_BHN)):
			if pre_Sta_BHN[i][2] == '  ':
				pre_Sta_BHN[i][2] = ''
			pre_Sta_BHN[i] = [pre_Sta_BHN[i][0], pre_Sta_BHN[i][1], pre_Sta_BHN[i][2], pre_Sta_BHN[i][3]]
			Sta_BHN.append(pre_Sta_BHN[i])
		
		
		file_BHZ = open(ls_event[l] + '/IRIS/info/iris_BHZ', 'r')
		
		pre_Sta_BHZ = file_BHZ.readlines()
		
		for i in range(0, len(pre_Sta_BHZ)):
			pre_Sta_BHZ[i] = pre_Sta_BHZ[i].split(',')
		
		for i in range(0, len(pre_Sta_BHZ)):
			if pre_Sta_BHZ[i][2] == '  ':
				pre_Sta_BHZ[i][2] = ''
			pre_Sta_BHZ[i] = [pre_Sta_BHZ[i][0], pre_Sta_BHZ[i][1], pre_Sta_BHZ[i][2], pre_Sta_BHZ[i][3]]
			Sta_BHZ.append(pre_Sta_BHZ[i])
	
		
		
		for i in range(0, len(all_iris_BHE)):
			if all_iris_BHE[i] != []:
				if all_iris_BHE[i][2] == '--':
					all_iris_BHE[i][2] = ''
		
		for i in range(0, len(all_iris_BHN)):
			if all_iris_BHN[i] != []:
				if all_iris_BHN[i][2] == '--':
					all_iris_BHN[i][2] = ''
				
		for i in range(0, len(all_iris_BHZ)):
			if all_iris_BHZ[i] != []:
				if all_iris_BHZ[i][2] == '--':
					all_iris_BHZ[i][2] = ''	 		
 		
 		common_BHE = []
 		
 		for i in range(0, len(all_iris_BHE)):
 			for j in range(0, len(Sta_BHE)):
 				if all_iris_BHE[i] == Sta_BHE[j]:
 					common_BHE.append(all_iris_BHE[i])
 	
 		num_j = []
 		for i in range(0, len(common_BHE)):
 			for j in range(0, len(all_iris_BHE)):
 				if common_BHE[i] == all_iris_BHE[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			all_iris_BHE[i] = []
 		
 		
 		Stas_req_BHE = []
 		
 		for i in all_iris_BHE:
 			if i != []:
 				Stas_req_BHE.append(i)
 				
 		
 		common_BHN = []
 		
 		for i in range(0, len(all_iris_BHN)):
 			for j in range(0, len(Sta_BHN)):
 				if all_iris_BHN[i] == Sta_BHN[j]:
 					common_BHN.append(all_iris_BHN[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHN)):
 			for j in range(0, len(all_iris_BHN)):
 				if common_BHN[i] == all_iris_BHN[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			all_iris_BHN[i] = []
 		
 		
 		Stas_req_BHN = []
 		
 		for i in all_iris_BHN:
 			if i != []:
 				Stas_req_BHN.append(i)
 				
 				
 		common_BHZ = []
 		
 		for i in range(0, len(all_iris_BHZ)):
 			for j in range(0, len(Sta_BHZ)):
 				if all_iris_BHZ[i] == Sta_BHZ[j]:
 					common_BHZ.append(all_iris_BHZ[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHZ)):
 			for j in range(0, len(all_iris_BHZ)):
 				if common_BHZ[i] == all_iris_BHZ[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			all_iris_BHZ[i] = []
 		
 		
 		Stas_req_BHZ = []
 		
 		for i in all_iris_BHZ:
 			if i != []:
 				Stas_req_BHZ.append(i)
 		
 		
 		for i in range(0, len(Stas_req_BHE)):
 			if Stas_req_BHE[i][2] == '':
 				Stas_req_BHE[i][2] = '--'
 		
 		for i in range(0, len(Stas_req_BHN)):
 			if Stas_req_BHN[i][2] == '':
 				Stas_req_BHN[i][2] = '--'
 		
 		for i in range(0, len(Stas_req_BHZ)):
 			if Stas_req_BHZ[i][2] == '':
 				Stas_req_BHZ[i][2] = '--'		
 		
 		
 		for i in events_all_file:
			if i['event_id'] == ls_event[l].split('/')[-1]:
				
				event_id = i['event_id']
				event_dp= i['depth']
				event_la= i['latitude']
				event_lo= i['longitude']
				event_mag= i['magnitude']
				event_origin = i['datetime']
				
				Address = ls_event[l]
				t1 = i['datetime']-input['t_before']
				t2 = i['datetime']+input['t_after']
				
		
		
		Exception_file = open(Address + '/' + '/IRIS/Excep_py/' + 'excep_iris_update', 'w')
		Exception_file.writelines('\n' + event_id + '\n')
		Exception_file.writelines('----------------------------UPDATE - IRIS----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		
		
		dic_BHE = {}		
				
		if input['BHE'] == 'Y':
					
			for i in range(0, len(Stas_req_BHE)):			
				
				print '------------------'
				print 'Updating - IRIS-BHE - ' + str(l) + ' -- ' + str(i) + ':'
				
				try:					
			
					client_iris = Client_iris()
							
					# BHE
					if input['waveform'] == 'Y':
							
						dummy = 'UPDATE-Waveform'
								
						client_iris.saveWaveform(Address + '/IRIS/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
							Stas_req_BHE[i][2], 'BHE', t1, t2)
								
						print "UPDATE - Saving Waveform for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"  
							
					if input['response'] == 'Y':
							
						dummy = 'UPDATE-Response'
								
						client_iris.saveResponse(Address + '/IRIS/Resp/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
							Stas_req_BHE[i][2], 'BHE', t1, t2)
								
						print "UPDATE - Saving Response for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHE[i][j][0], \
						station=Networks_iris_BHE[i][j][1], location=Networks_iris_BHE[i][j][2], \
						channel="BHE", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
					
					avail = client_iris.availability(network=Stas_req_BHE[i][0], \
						station=Stas_req_BHE[i][1], location=Stas_req_BHE[i][2], \
						channel="BHE", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					dic_BHE[i] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', 'SAC')
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
					
					st[0].stats['sac']['stla'] = dic_BHE[i]['Latitude']
					st[0].stats['sac']['stlo'] = dic_BHE[i]['Longitude']
					st[0].stats['sac']['stel'] = dic_BHE[i]['Elevation']
					
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', 'SAC')
					
					Syn_file = open(Address + '/IRIS/info/' + 'iris_BHE', 'a')
					syn = dic_BHE[i]['Network'] + ',' + dic_BHE[i]['Station'] + ',' + \
						dic_BHE[i]['Location'] + ',' + dic_BHE[i]['Channel'] + ',' + dic_BHE[i]['Latitude'] + \
						',' + dic_BHE[i]['Longitude'] + ',' + dic_BHE[i]['Elevation'] + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE'
					
					Exception_file = open(Address + '/IRIS/Excep_py/' + 'excep_iris_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/info/' + 'avail_iris_BHE', 'a')
		pickle.dump(dic_BHE, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/info/' + 'report_st', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHE) for event' + '-' + str(l) + ': ' + str(len(dic_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
						
				
		dic_BHN = {}		
				
		if input['BHN'] == 'Y':
					
			for i in range(0, len(Stas_req_BHN)):			
					
				print '------------------'
				print 'Updating - IRIS-BHN - ' + str(l) + ' -- ' + str(i) + ':'
					
				try:					
			
					client_iris = Client_iris()
							
					# BHN
					if input['waveform'] == 'Y':
							
						dummy = 'UPDATE-Waveform'
								
						client_iris.saveWaveform(Address + '/IRIS/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
							Stas_req_BHN[i][2], 'BHN', t1, t2)
								
						print "UPDATE - Saving Waveform for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"  
							
					if input['response'] == 'Y':
							
						dummy = 'UPDATE-Response'
								
						client_iris.saveResponse(Address + '/IRIS/Resp/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
							Stas_req_BHN[i][2], 'BHN', t1, t2)
								
						print "UPDATE - Saving Response for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHN[i][j][0], \
						station=Networks_iris_BHN[i][j][1], location=Networks_iris_BHN[i][j][2], \
						channel="BHN", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
							
					avail = client_iris.availability(network=Stas_req_BHN[i][0], \
						station=Stas_req_BHN[i][1], location=Stas_req_BHN[i][2], \
						channel="BHN", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					dic_BHN[i] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', 'SAC')
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
					
					st[0].stats['sac']['stla'] = dic_BHN[i]['Latitude']
					st[0].stats['sac']['stlo'] = dic_BHN[i]['Longitude']
					st[0].stats['sac']['stel'] = dic_BHN[i]['Elevation']
					
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', 'SAC')
					
					Syn_file = open(Address + '/IRIS/info/' + 'iris_BHN', 'a')
					syn = dic_BHN[i]['Network'] + ',' + dic_BHN[i]['Station'] + ',' + \
						dic_BHN[i]['Location'] + ',' + dic_BHN[i]['Channel'] + ',' + dic_BHN[i]['Latitude'] + \
						',' + dic_BHN[i]['Longitude'] + ',' + dic_BHN[i]['Elevation'] + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN'
					
					Exception_file = open(Address + '/IRIS/Excep_py/' + 'excep_iris_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/info/' + 'avail_iris_BHN', 'a')
		pickle.dump(dic_BHN, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/info/' + 'report_st', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHN) for event' + '-' + str(l) + ': ' + str(len(dic_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()				
					
					
		dic_BHZ = {}		
				
		if input['BHZ'] == 'Y':
					
			for i in range(0, len(Stas_req_BHZ)):			
					
				print '------------------'
				print 'Updating - IRIS-BHZ - ' + str(l) + ' -- ' + str(i) + ':'
					
				try:					
			
					client_iris = Client_iris()
							
					# BHZ
					if input['waveform'] == 'Y':
							
						dummy = 'UPDATE-Waveform'
								
						client_iris.saveWaveform(Address + '/IRIS/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
							Stas_req_BHZ[i][2], 'BHZ', t1, t2)
								
						print "UPDATE - Saving Waveform for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"  
								
					if input['response'] == 'Y':
					
						dummy = 'UPDATE-Response'
								
						client_iris.saveResponse(Address + '/IRIS/Resp/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
							Stas_req_BHZ[i][2], 'BHZ', t1, t2)
								
						print "UPDATE - Saving Response for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
							
					'''
					dummy = 'sacpz'
							
					import ipdb; ipdb.set_trace()
							
					sacpz = client_iris.sacpz(network=Networks_iris_BHZ[i][j][0], \
						station=Networks_iris_BHZ[i][j][1], location=Networks_iris_BHZ[i][j][2], \
						channel="BHZ", starttime=t[i]-input['t_before'], endtime=t[i]+input['t_after'])
					'''
					dummy = 'UPDATE-availability'
							
					avail = client_iris.availability(network=Stas_req_BHZ[i][0], \
						station=Stas_req_BHZ[i][1], location=Stas_req_BHZ[i][2], \
						channel="BHZ", starttime=t1, endtime=t2, output = 'xml')
							
							
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
					dic_BHZ[i] ={'Info': Sta_net_code + '.' + Sta_sta_code + '.' + Sta_loc_code + '.' + Sta_chan_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code, 'Elevation': Sta_Elevation}
					
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', 'SAC')
					st = read(Address + '/IRIS/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
					
					st[0].stats['sac']['stla'] = dic_BHZ[i]['Latitude']
					st[0].stats['sac']['stlo'] = dic_BHZ[i]['Longitude']
					st[0].stats['sac']['stel'] = dic_BHZ[i]['Elevation']
					
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/IRIS/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', 'SAC')
					
					Syn_file = open(Address + '/IRIS/info/' + 'iris_BHZ', 'a')
					syn = dic_BHZ[i]['Network'] + ',' + dic_BHZ[i]['Station'] + ',' + \
						dic_BHZ[i]['Location'] + ',' + dic_BHZ[i]['Channel'] + ',' + dic_BHZ[i]['Latitude'] + \
						',' + dic_BHZ[i]['Longitude'] + ',' + dic_BHZ[i]['Elevation'] + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ'
					
					Exception_file = open(Address + '/IRIS/Excep_py/' + 'excep_iris_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' +	'---' + str(e) + '\n'
							
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
		Station_file = open(Address + '/IRIS/info/' + 'avail_iris_BHZ', 'a')
		pickle.dump(dic_BHZ, Station_file)
		Station_file.close()
				
				
		Report = open(Address + '/IRIS/info/' + 'report_st', 'a')
		rep1 = 'UPDATE - IRIS-Saved stations (BHZ) for event' + '-' + str(l) + ': ' + str(len(dic_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()			
			
	t_update_2 = datetime.now()
		
	t_update = t_update_2 - t_update_1
	
	Report = open(Address + '/IRIS/info/' + 'report_st', 'a')
	Report.writelines('----------------------------------' + '\n')
	rep1 = 'Time for updating the IRIS folder: ' + str(t_update) + '\n'
	Report.writelines(rep1)
	Report.writelines('----------------------------------' + '\n')
	Report.close()	
		
	print 'Time for Updating: (IRIS)'
	print t_update

###################################################### update_ARC ######################################################

def update_ARC(input):
	
	"""
	Updating the station folders from ArcLink
	Attention: This module update all station folders for all events in one directory.
	-----------------
	Problems:
	- Exception_file_ARC_update OR Exception_file_ARC?
	"""
	
	t_update_1 = datetime.now()
	
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
	
	add_ARC_events = []
	for i in pre_ls_event:
		add_ARC_events.append(i + '/EVENT/event_list')
		
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
		
		ls_stas_open = open(ls_event[l] + '/ARC/info/All_ARC_Stations_BHE', 'r')
		All_ARC_Stations_BHE = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/info/All_ARC_Stations_BHN', 'r')
		All_ARC_Stations_BHN = pickle.load(ls_stas_open)
		ls_stas_open.close()
		
		ls_stas_open = open(ls_event[l] + '/ARC/info/All_ARC_Stations_BHZ', 'r')
		All_ARC_Stations_BHZ = pickle.load(ls_stas_open)
		ls_stas_open.close()
		'''
		upfile = open(ls_event[l] + '/ARC/info/' + 'UPDATE', 'w')
		upfile.writelines('\n' + ls_event[l].split('/')[-1] + '\n')
		upfile.writelines('----------------------------ARC----------------------------'+ '\n')
		upfile.writelines('----------------------------UPDATED----------------------------'+ '\n')
		upfile.close()
		'''
		
		#------------------------------------------------------------------------------------
		exception_arc = open(ls_event[l] + '/ARC/Excep_py/' + 'Exception_file_ARC', 'r')
		excepts = exception_arc.readlines()
		
		for i in range(0, len(excepts)):
   			excepts[i] = excepts[i].split('---')
   		
   		Access_denied = []
   		No_data = []
   		
   		for i in range(2, len(excepts)):
			if excepts[i][3] == 'DENIED access denied for user ObsPy\n':
				Access_denied.append(excepts[i][2])
				
			if excepts[i][3] == 'No data available\n':
				No_data.append(excepts[i][2])
				
		
		for i in range(0, len(Access_denied)):
			Access_denied[i] = Access_denied[i].split('.')
		
		
		for i in range(0, len(No_data)):
			No_data[i] = No_data[i].split('.')
		
		#------------------------------------------------------------------------------------
		pre_Sta_BHE = []
		pre_Sta_BHN = []
		pre_Sta_BHZ = []
		
		Sta_BHE = []
		Sta_BHN = []
		Sta_BHZ = []
		
		
		file_BHE = open(ls_event[l] + '/ARC/info/iris_BHE', 'r')
		
		pre_Sta_BHE = file_BHE.readlines()
		
		for i in range(0, len(pre_Sta_BHE)):
			pre_Sta_BHE[i] = pre_Sta_BHE[i].split(',')
		
		for i in range(0, len(pre_Sta_BHE)):
			if pre_Sta_BHE[i][2] == '  ':
				pre_Sta_BHE[i][2] = ''
			pre_Sta_BHE[i] = [pre_Sta_BHE[i][0], pre_Sta_BHE[i][1], pre_Sta_BHE[i][2], pre_Sta_BHE[i][3]]
			Sta_BHE.append(pre_Sta_BHE[i])
		
		
		file_BHN = open(ls_event[l] + '/ARC/info/iris_BHN', 'r')
		
		pre_Sta_BHN = file_BHN.readlines()
		
		for i in range(0, len(pre_Sta_BHN)):
			pre_Sta_BHN[i] = pre_Sta_BHN[i].split(',')
		
		for i in range(0, len(pre_Sta_BHN)):
			if pre_Sta_BHN[i][2] == '  ':
				pre_Sta_BHN[i][2] = ''
			pre_Sta_BHN[i] = [pre_Sta_BHN[i][0], pre_Sta_BHN[i][1], pre_Sta_BHN[i][2], pre_Sta_BHN[i][3]]
			Sta_BHN.append(pre_Sta_BHN[i])
		
		
		file_BHZ = open(ls_event[l] + '/ARC/info/iris_BHZ', 'r')
		
		pre_Sta_BHZ = file_BHZ.readlines()
		
		for i in range(0, len(pre_Sta_BHZ)):
			pre_Sta_BHZ[i] = pre_Sta_BHZ[i].split(',')
		
		for i in range(0, len(pre_Sta_BHZ)):
			if pre_Sta_BHZ[i][2] == '  ':
				pre_Sta_BHZ[i][2] = ''
			pre_Sta_BHZ[i] = [pre_Sta_BHZ[i][0], pre_Sta_BHZ[i][1], pre_Sta_BHZ[i][2], pre_Sta_BHZ[i][3]]
			Sta_BHZ.append(pre_Sta_BHZ[i])
			
		
 		common_BHE = []
 		
 		for i in range(0, len(All_ARC_Stations_BHE)):
 			for j in range(0, len(Sta_BHE)):
 				if All_ARC_Stations_BHE[i] == Sta_BHE[j]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHE[i] == Access_denied[m]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHE[i] == No_data[n]:
 					common_BHE.append(All_ARC_Stations_BHE[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHE)):
 			for j in range(0, len(All_ARC_Stations_BHE)):
 				if common_BHE[i] == All_ARC_Stations_BHE[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHE[i] = []
 		
 		
 		Stas_req_BHE = []
 		
 		for i in All_ARC_Stations_BHE:
 			if i != []:
 				Stas_req_BHE.append(i)
 				
 		common_BHN = []
 		
 		for i in range(0, len(All_ARC_Stations_BHN)):
 			for j in range(0, len(Sta_BHN)):
 				if All_ARC_Stations_BHN[i] == Sta_BHN[j]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHN[i] == Access_denied[m]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHN[i] == No_data[n]:
 					common_BHN.append(All_ARC_Stations_BHN[i])
 		
 		num_j = []
 		for i in range(0, len(common_BHN)):
 			for j in range(0, len(All_ARC_Stations_BHN)):
 				if common_BHN[i] == All_ARC_Stations_BHN[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHN[i] = []
 		
 		
 		Stas_req_BHN = []
 		
 		for i in All_ARC_Stations_BHN:
 			if i != []:
 				Stas_req_BHN.append(i)
 				
 				
 		common_BHZ = []
 		
 		for i in range(0, len(All_ARC_Stations_BHZ)):
 			for j in range(0, len(Sta_BHZ)):
 				if All_ARC_Stations_BHZ[i] == Sta_BHZ[j]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 			
 			for m in range(0, len(Access_denied)):
 				if All_ARC_Stations_BHZ[i] == Access_denied[m]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 			
 			for n in range(0, len(No_data)):
 				if All_ARC_Stations_BHZ[i] == No_data[n]:
 					common_BHZ.append(All_ARC_Stations_BHZ[i])
 				
 		num_j = []
 		for i in range(0, len(common_BHZ)):
 			for j in range(0, len(All_ARC_Stations_BHZ)):
 				if common_BHZ[i] == All_ARC_Stations_BHZ[j]:
 					num_j.append(j)
 		
 		num_j.reverse()
 		
 		for i in num_j:
 			All_ARC_Stations_BHZ[i] = []
 		
 		
 		Stas_req_BHZ = []
 		
 		for i in All_ARC_Stations_BHZ:
 			if i != []:
 				Stas_req_BHZ.append(i)
 		
 		for i in events_all_file:
			if i['event_id'] == ls_event[l].split('/')[-1]:
				
				event_id = i['event_id']
				event_dp= i['depth']
				event_la= i['latitude']
				event_lo= i['longitude']
				event_mag= i['magnitude']
				event_origin = i['datetime']
				
				Address = ls_event[l]
				t1 = i['datetime']-input['t_before']
				t2 = i['datetime']+input['t_after']
				
		
		
		Exception_file = open(Address + '/' + '/ARC/Excep_py/' + 'Exception_file_ARC_update', 'w')
		Exception_file.writelines('\n' + event_id + '\n')
		Exception_file.writelines('----------------------------UPDATE - ARC----------------------------'+ '\n')
		Exception_file.writelines('----------------------------EXCEPTION----------------------------'+ '\n')
		
		
		#import ipdb; ipdb.set_trace()
		inv_BHE = {}
		
		if input['BHE'] == 'Y':
			
			for i in range(0, len(Stas_req_BHE)):
				
				print '------------------'
				print 'Updating - ArcLink-BHE - ' + str(l) + ' -- ' + str(i) + ':'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHE
					if input['waveform'] == 'Y':
					
						dummy = 'UPDATE-Waveform'
						
						client_arclink.saveWaveform(Address + '/ARC/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
							Stas_req_BHE[i][2], 'BHE', t1, t2)
						
						print "UPDATE - Saving Waveform for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"  
										
					if input['response'] == 'Y':
						
						dummy = 'UPDATE-Response'
						
						client_arclink.saveResponse(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
							Stas_req_BHE[i][2], 'BHE', t1, t2)
						
						sp = Parser(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
						
						sp.writeRESP(Address + '/ARC/Resp')
						
						
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')	
						'''	
						
						print "UPDATE - Saving Response for: " + Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
						
					
					dummy = 'UPDATE-Inventory'
					
					inv_BHE[i] = client_arclink.getInventory(Stas_req_BHE[i][0], Stas_req_BHE[i][1], \
						Stas_req_BHE[i][2], 'BHE')
					
					dum = Stas_req_BHE[i][0] + '.' + Stas_req_BHE[i][1]
									
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', 'SAC')
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE')
					
					if inv_BHE[i][dum]['latitude'] != None:
						st[0].stats['sac']['stla'] = inv_BHE[i][dum]['latitude']
					if inv_BHE[i][dum]['longitude'] != None:
						st[0].stats['sac']['stlo'] = inv_BHE[i][dum]['longitude']
					if inv_BHE[i][dum]['elevation'] != None:
						st[0].stats['sac']['stel'] = inv_BHE[i][dum]['elevation']
					if inv_BHE[i][dum]['depth'] != None:
						st[0].stats['sac']['stdp'] = inv_BHE[i][dum]['depth']
					
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
							Stas_req_BHE[i][2] + '.' + 'BHE', 'SAC')
					
					Syn_file = open(Address + '/ARC/info/' + 'iris_BHE', 'a')
					syn = Stas_req_BHE[i][0] + ',' + Stas_req_BHE[i][1] + ',' + \
					Stas_req_BHE[i][2] + ',' + Stas_req_BHE[i][3] + ',' + str(inv_BHE[i][dum]['latitude']) + \
						',' + str(inv_BHE[i][dum]['longitude']) + ',' + str(inv_BHE[i][dum]['elevation']) + ',' + \
						str(inv_BHE[i][dum]['depth']) + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHE[i][0] +	'.' + Stas_req_BHE[i][1] + \
						'.' +Stas_req_BHE[i][2] + '.' + 'BHE'
					
					Exception_file = open(Address + '/ARC/Excep_py/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHE[i][0] + \
						'.' + Stas_req_BHE[i][1] + '.' + \
						Stas_req_BHE[i][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/info/' + 'Avail_ARC_Stations_BHE', 'a')
		pickle.dump(inv_BHE, Station_file)
		Station_file.close()
		
		
		Report = open(Address + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHE) for event' + '-' + str(i) + ': ' + str(len(inv_BHE)) + '\n'
		Report.writelines(rep1)
		Report.close()	
				
		
		inv_BHN = {}
		
		if input['BHN'] == 'Y':
			
			for i in range(0, len(Stas_req_BHN)):
				
				print '------------------'
				print 'Updating - ArcLink-BHN - ' + str(l) + ' -- ' + str(i) + ':'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHN
					if input['waveform'] == 'Y':
							
						dummy = 'UPDATE-Waveform'
						
						client_arclink.saveWaveform(Address + '/ARC/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
							Stas_req_BHN[i][2], 'BHN', t1, t2)
						
						print "UPDATE - Saving Waveform for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"  
										
					if input['response'] == 'Y':
						
						dummy = 'UPDATE-Response'
						
						client_arclink.saveResponse(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
							Stas_req_BHN[i][2], 'BHN', t1, t2)
						
						
						sp = Parser(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
						
						sp.writeRESP(Address + '/ARC/Resp')
						
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')	
						'''	
						
						print "UPDATE - Saving Response for: " + Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
							
						
					dummy = 'UPDATE-Inventory'
					
					inv_BHN[i] = client_arclink.getInventory(Stas_req_BHN[i][0], Stas_req_BHN[i][1], \
						Stas_req_BHN[i][2], 'BHN')
					
					dum = Stas_req_BHN[i][0] + '.' + Stas_req_BHN[i][1]
									
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', 'SAC')
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN')
					
					if inv_BHN[i][dum]['latitude'] != None:
						st[0].stats['sac']['stla'] = inv_BHN[i][dum]['latitude']
					if inv_BHN[i][dum]['longitude'] != None:
						st[0].stats['sac']['stlo'] = inv_BHN[i][dum]['longitude']
					if inv_BHN[i][dum]['elevation'] != None:
						st[0].stats['sac']['stel'] = inv_BHN[i][dum]['elevation']
					if inv_BHN[i][dum]['depth'] != None:
						st[0].stats['sac']['stdp'] = inv_BHN[i][dum]['depth']
					
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
							Stas_req_BHN[i][2] + '.' + 'BHN', 'SAC')
					
					Syn_file = open(Address + '/ARC/info/' + 'iris_BHN', 'a')
					syn = Stas_req_BHN[i][0] + ',' + Stas_req_BHN[i][1] + ',' + \
						Stas_req_BHN[i][2] + ',' + Stas_req_BHN[i][3] + ',' + str(inv_BHN[i][dum]['latitude']) + \
						',' + str(inv_BHN[i][dum]['longitude']) + ',' + str(inv_BHN[i][dum]['elevation']) + ',' + \
						str(inv_BHN[i][dum]['depth']) + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHN[i][0] +	'.' + Stas_req_BHN[i][1] + \
						'.' +Stas_req_BHN[i][2] + '.' + 'BHN'
					
					Exception_file = open(Address + '/ARC/Excep_py/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHN[i][0] + \
						'.' + Stas_req_BHN[i][1] + '.' + \
						Stas_req_BHN[i][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/info/' + 'Avail_ARC_Stations_BHN', 'a')
		pickle.dump(inv_BHN, Station_file)
		Station_file.close()
			
			
		Report = open(Address + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHN) for event' + '-' + str(i) + ': ' + str(len(inv_BHN)) + '\n'
		Report.writelines(rep1)
		Report.close()			
				
		
		inv_BHZ = {}
		
		if input['BHZ'] == 'Y':
			
			for i in range(0, len(Stas_req_BHZ)):
				
				print '------------------'
				print 'Updating - ArcLink-BHZ - ' + str(l) + ' -- ' + str(i) + ':'
				
				try:
					
					client_arclink = Client_arclink(timeout=5)
					
					# BHZ
					if input['waveform'] == 'Y':
							
						dummy = 'UPDATE-Waveform'
						
						client_arclink.saveWaveform(Address + '/ARC/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
							Stas_req_BHZ[i][2], 'BHZ', t1, t2)
						
						print "UPDATE - Saving Waveform for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"  
						
					if input['response'] == 'Y':
											
						dummy = 'UPDATE-Response'
						
						client_arclink.saveResponse(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
							Stas_req_BHZ[i][2], 'BHZ', t1, t2)
						
						
						sp = Parser(Address + '/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
						
						sp.writeRESP(Address + '/ARC/Resp')
						
						'''
						pars = Parser()
							
						pars.read(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
						
						pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
							'/ARC/Resp/' + 'RESP' + '.' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')	
						'''	
						
						print "UPDATE - Saving Response for: " + Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
							
						
					dummy = 'UPDATE-Inventory'
					
					inv_BHZ[i] = client_arclink.getInventory(Stas_req_BHZ[i][0], Stas_req_BHZ[i][1], \
						Stas_req_BHZ[i][2], 'BHZ')
					
					dum = Stas_req_BHZ[i][0] + '.' + Stas_req_BHZ[i][1]
									
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', 'SAC')
					st = read(Address + '/ARC/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ')
					
					if inv_BHZ[i][dum]['latitude'] != None:
						st[0].stats['sac']['stla'] = inv_BHZ[i][dum]['latitude']
					if inv_BHZ[i][dum]['longitude'] != None:
						st[0].stats['sac']['stlo'] = inv_BHZ[i][dum]['longitude']
					if inv_BHZ[i][dum]['elevation'] != None:
						st[0].stats['sac']['stel'] = inv_BHZ[i][dum]['elevation']
					if inv_BHZ[i][dum]['depth'] != None:
						st[0].stats['sac']['stdp'] = inv_BHZ[i][dum]['depth']
						
					st[0].stats['sac']['evla'] = event_la
					st[0].stats['sac']['evlo'] = event_lo
					st[0].stats['sac']['evdp'] = event_dp
					st[0].stats['sac']['mag'] = event_mag
					
					st[0].write(Address + '/ARC/BH_RAW/' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
							Stas_req_BHZ[i][2] + '.' + 'BHZ', 'SAC')
					
					Syn_file = open(Address + '/ARC/info/' + 'iris_BHZ', 'a')
					syn = Stas_req_BHZ[i][0] + ',' + Stas_req_BHZ[i][1] + ',' + \
						Stas_req_BHZ[i][2] + ',' + Stas_req_BHZ[i][3] + ',' + str(inv_BHZ[i][dum]['latitude']) + \
						',' + str(inv_BHZ[i][dum]['longitude']) + ',' + str(inv_BHZ[i][dum]['elevation']) + ',' + \
						str(inv_BHZ[i][dum]['depth']) + ',' + events[l]['event_id'] + ',' + str(events[l]['latitude']) \
						 + ',' + str(events[l]['longitude']) + ',' + str(events[l]['depth']) + ',' + '\n'
					Syn_file.writelines(syn)
					Syn_file.close()
					
					print "UPDATE - Saving Station  for: " + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + "  ---> DONE"
					
					#client_arclink.close()
					
				except Exception, e:	
					
					print dummy + '---' + Stas_req_BHZ[i][0] +	'.' + Stas_req_BHZ[i][1] + \
						'.' +Stas_req_BHZ[i][2] + '.' + 'BHZ'
					
					Exception_file = open(Address + '/ARC/Excep_py/' + 'Exception_file_ARC_update', 'a')

					ee = dummy + '---' + str(l) + '-' + str(i) + '---' + Stas_req_BHZ[i][0] + \
						'.' + Stas_req_BHZ[i][1] + '.' + \
						Stas_req_BHZ[i][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
					
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
		
		
		Station_file = open(Address + '/ARC/info/' + 'Avail_ARC_Stations_BHZ', 'a')
		pickle.dump(inv_BHZ, Station_file)
		Station_file.close()
			
			
		Report = open(Address + '/ARC/info/' + 'report_st', 'a')
		rep1 = 'ArcLink-Saved stations (BHZ) for event' + '-' + str(i) + ': ' + str(len(inv_BHZ)) + '\n'
		Report.writelines(rep1)
		Report.close()	

	
	t_update_2 = datetime.now()
		
	t_update = t_update_2 - t_update_1
	
	Report = open(Address + '/ARC/info/' + 'report_st', 'a')
	Report.writelines('----------------------------------' + '\n')
	rep1 = 'Time for updating the ARC folder: ' + str(t_update) + '\n'
	Report.writelines(rep1)
	Report.writelines('----------------------------------' + '\n')
	Report.close()	
		
	print 'Time for Updating: (ARC)'
	print t_update

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
