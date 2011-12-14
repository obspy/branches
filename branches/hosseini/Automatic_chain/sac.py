import commands
import os
import glob

address = '/media/Elements/TEST_SUMATRA_tarje/2009-09-29_2009-10-01_7.4_8.0/20090930_0000037/'

input_file = open(address + 'IRIS/info/iris_BHZ')

inp = input_file.readlines()
for i in range(0, len(inp)):
	inp[i] = inp[i].split(',')

raw_file = []
resp_file = []

for i in range(0, len(inp)):
	if inp[i][2] == '  ':
		inp[i][2] = ''
	raw_file.append(glob.glob(address + 'IRIS/BH_RAW/' + inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3])) 
	resp_file.append(glob.glob(address + 'IRIS/Resp/RESP.' + inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3]))

for i in range(0, len(raw_file)):
	#import ipdb; ipdb.set_trace()
	print str(i) + '/' + str(len(raw_file))
	i1 = raw_file[i][0]
	i2 = resp_file[i][0]
	i4 = inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3]
	commands.getoutput('./sac.sh' + ' ' + i1 + ' ' + i2 + ' ' + address + ' ' + i4)
	
	

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------
#   Filename:  DMT_inst.py
#   Author:    S. Kasra Hosseini zad
#   Email:     hosseini@geophysik.uni-muenchen.de
#
#   Copyright (C) 2011 Seyed Kasra Hosseini zad
#-------------------------------------------------------------------


"""
DMT_inst (Data Management Tool - Instrument Correction)

Goal: Instrument Correction of Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""

#for debugging: import ipdb; ipdb.set_trace()


# ------------------------Import required Modules (Python and Obspy)-------------

"""
Required Python and Obspy modules will be imported in this part.
"""

from obspy.signal import seisSim, invsim
from obspy.core import read

from datetime import datetime
import numpy as np
import os
import sys
import ConfigParser
import pickle

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def DMT_inst():
	
	t1_pro = datetime.now()
	
	print '--------------------------------------------------------------------------------'
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'DMT_inst ' + reset + '(' + bold + 'D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' \
		+ reset + 'ool' + '-' + bold + 'I' + reset + 'nstrument' + bold + 'C' + reset + 'orrection)' + reset + '\n'
	print '\t' + 'Instrument Correction of Large Seismic Datasets' + '\n'
	print ':copyright:'
	print 'The ObsPy Development Team (devs@obspy.org)' + '\n'
	print ':license:'
	print 'GNU Lesser General Public License, Version 3'
	print '(http://www.gnu.org/copyleft/lesser.html)'
	print '--------------------------------------------------------------------------------'
	
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()
	
	# ------------------------IRIS------------------------------------------------
	if input['IRIS_inst'] == 'Y':
		
		print '\n' + '***********************************************************************************************'
		print 'IRIS -- Instrument Correction'
		print '***********************************************************************************************'
		
		IRIS(input)
	
	# ------------------------Arclink------------------------------------------------
	if input['ArcLink_inst'] == 'Y':
			
		print '\n' + '************************************************************************************************'
		print 'ArcLink -- Instrument Correction'
		print '************************************************************************************************'
				
		ARC(input)
	
	# --------------------------------------------------------
	print '--------------------------------------------------------------------------------'
	print 'Thanks for using:' + '\n' 
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'DMT_inst ' + reset + '(' + bold + 'D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' \
		+ reset + 'ool' + '-' + bold + 'I' + reset + 'nstrument' + bold + 'C' + reset + 'orrection)' + reset + '\n'
	
	print "Total Time:"
	print datetime.now() - t1_pro 
	print '--------------------------------------------------------------------------------'
	
	
###################################################### read_input ######################################################

def read_input():	
	
	"""
	Read inputs from INPUT.cfg file.
	This module will read the INPUT.cfg file which is located in the same folder as ObsPyDMT.py
	Please note that if you choose (nodes = Y) then:
	* min_datetime
	* max_datetime
	* min_magnitude
	* max_magnitude
	will be selected based on INPUT-Periods file.
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
	input['input_period'] = config.get('Request', 'input_period')
	input['IRIS'] = config.get('Request', 'IRIS')
	input['ArcLink'] = config.get('Request', 'ArcLink')
	input['time_iris'] = config.get('Request', 'time_iris')
	input['time_arc'] = config.get('Request', 'time_arc')
	
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
	
	input['IRIS_inst'] = config.get('instrument_correction', 'IRIS_inst')
	input['ArcLink_inst'] = config.get('instrument_correction', 'ArcLink_inst')
	input['corr_unit'] = config.get('instrument_correction', 'corr_unit')
	input['pre_filt'] = config.get('instrument_correction', 'pre_filter')
	input['pre_filt'] = tuple(float(s) for s in input['pre_filt'][1:-1].split(','))
	
	input['phase'] = config.get('select_seismogram', 'phase')
	input['phase'] = list(s for s in input['phase'][1:-1].split(','))
	input['freq'] = config.getfloat('select_seismogram', 'freq')
	input['model'] = config.get('select_seismogram', 'model')
	
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

###################################################### inst_IRIS ######################################################

def IRIS(input):
	
	"""
	Call "inst_IRIS" function based on your channel request.
	"""

	if input['BHE'] == 'Y':
		inst_IRIS(input, channel = 'BHE', interactive = input['inter_address'])
	
	if input['BHN'] == 'Y':
		inst_IRIS(input, channel = 'BHN', interactive = input['inter_address'])
	
	if input['BHZ'] == 'Y':
		inst_IRIS(input, channel = 'BHZ', interactive = input['inter_address'])

	print "-------------------------------------------------"
	print 'IRIS Instrument Correction is DONE'
	print "-------------------------------------------------"

###################################################### inst_IRIS ######################################################
	
def inst_IRIS(input, channel, interactive = 'N'):
	
	"""
	
	"""
	
	t_inst_1 = datetime.now()
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter

	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	input_file = []
	
	for l in range(0, len_events):
		
		input_file.append(open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/iris_' + channel))
		
		try:
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_SAC')
			
		except Exception, e:
			print '********************************************'
			print e
			print '********************************************'
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_SAC'
			print "exists in your directory..."
			print 'The program will continue in the same folder!'
			
		input_sta = input_file[l].readlines()
		
		for i in range(0, len(input_sta)):
			input_sta[i] = input_sta[i].split(',')
			if input_sta[i][2] == '  ':
				input_sta[i][2] = ''
				
		BH_raw_file = []
		resp_file = []

		for i in range(0, len(input_sta)):
			BH_raw_file.append(Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_RAW/' + \
				input_sta[i][0] + '.' + input_sta[i][1] + '.' + input_sta[i][2] + '.' + input_sta[i][3]) 
		
		for k in range(0, len(BH_raw_file)):
			
			print '********************************************'
			print str(k+1) + '/' + str(len(BH_raw_file))
			
			tr_tmp = read(BH_raw_file[k])
			tr = tr_tmp[0]
	
			resp_file = Address_events + '/' + events[l]['event_id'] + '/IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print 'Response file:'
			print resp_file
			
			i1 = BH_raw_file[k][0]
			i2 = resp_file
			i3 = Address_events + '/' + events[l]['event_id']
			i4 = BH_raw_file[k][0] + '.' + BH_raw_file[k][1] + '.' + BH_raw_file[k][2] + '.' + BH_raw_file[k][3]
			commands.getoutput('./sac.sh' + ' ' + i1 + ' ' + i2 + ' ' + i3 + ' ' + i4)
			'''
			check this out:
			i5 = 0.008
			i6 = 0.012
			i7 = 3.0
			i8 = 4.0
			commands.getoutput('./sac.sh' + ' ' + i1 + ' ' + i2 + ' ' + i3 + ' ' + i4 + ' ' + i5\
				+ ' ' + i6 + ' ' + i7 + ' ' + i8)
			'''
	
	
	t_inst_2 = datetime.now()
	
	print '*********************************************************************'
	print 'Time passed for Instrument Correction of ' + channel + ' :'
	print t_inst_2 - t_inst_1
	print '*********************************************************************'
