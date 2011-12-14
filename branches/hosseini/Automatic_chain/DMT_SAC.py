#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------
#   Filename:  DMT_SAC.py
#   Author:    S. Kasra Hosseini zad
#   Email:     hosseini@geophysik.uni-muenchen.de
#
#   Copyright (C) 2011 Seyed Kasra Hosseini zad
#-------------------------------------------------------------------


"""
DMT_SAC (Data Management Tool - SAC [Instrument Correction])

Goal: Instrument Correction of Large Seismic Datasets using SAC

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

from obspy.core import read

from datetime import datetime
import os
import sys
import ConfigParser
import pickle
import commands
import glob

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def DMT_SAC():
	
	t1_pro = datetime.now()
	
	print '--------------------------------------------------------------------------------'
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t' + bold + 'DMT_SAC ' + reset + '(' + bold + 'D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' \
		+ reset + 'ool' + '-' + bold + 'SAC' + reset + ')' + reset + '\n'
	print '\t' + 'Instrument Correction of Large Seismic Datasets using SAC' + '\n'
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
	print '\t\t' + bold + 'DMT_SAC ' + reset + '(' + bold + 'D' + reset + 'ata ' + bold + 'M' + reset + 'anagement ' + bold + 'T' \
		+ reset + 'ool' + '-' + bold + 'SAC' + reset + ')' + reset + '\n'
	
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
	
	input['IRIS'] = config.get('Request', 'IRIS')
	input['ArcLink'] = config.get('Request', 'ArcLink')
	
	input['BHE'] = config.get('specifications_request', 'BHE')
	input['BHN'] = config.get('specifications_request', 'BHN')
	input['BHZ'] = config.get('specifications_request', 'BHZ')
	input['other'] = config.get('specifications_request', 'other')
	
	input['TEST'] = config.get('test', 'TEST')
	input['TEST_no'] = config.getint('test', 'TEST_no')
	
	input['email'] = config.get('email', 'email')
	input['email_address'] = config.get('email', 'email_address')
	
	input['report'] = config.get('report', 'report')
	
	input['IRIS_inst'] = config.get('instrument_correction', 'IRIS_inst')
	input['ArcLink_inst'] = config.get('instrument_correction', 'ArcLink_inst')
	input['corr_unit'] = config.get('instrument_correction', 'corr_unit')
	input['pre_filt'] = config.get('instrument_correction', 'pre_filter')
	input['pre_filt'] = tuple(float(s) for s in input['pre_filt'][1:-1].split(','))
	
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
	Apply Instrument Coorection on all available stations in the folder
	This scrips loads "SAC" program for this reason
	Please refer to DMT_SAC.sh for more info
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
			commands.getoutput('./DMT_SAC.sh' + ' ' + i1 + ' ' + i2 + ' ' + i3 + ' ' + i4)
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

###################################################### inst_IRIS ######################################################

def ARC(input):
	
	"""
	Call "inst_ARC" function based on your channel request.
	"""

	if input['BHE'] == 'Y':
		inst_ARC(input, channel = 'BHE', interactive = input['inter_address'])
	
	if input['BHN'] == 'Y':
		inst_ARC(input, channel = 'BHN', interactive = input['inter_address'])
	
	if input['BHZ'] == 'Y':
		inst_ARC(input, channel = 'BHZ', interactive = input['inter_address'])

	print "-------------------------------------------------"
	print 'ARC Instrument Correction is DONE'
	print "-------------------------------------------------"

###################################################### inst_ARC ######################################################
	
def inst_ARC(input, channel, interactive = 'N'):
		
	"""
	Apply Instrument Coorection on all available stations in the folder
	This scrips loads "SAC" program for this reason
	Please refer to DMT_SAC.sh for more info
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
		
		input_file.append(open(Address_events + '/' + events[l]['event_id'] + '/ARC/info/arc_' + channel))
		
		try:
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/ARC/BH_SAC')
			
		except Exception, e:
			print '********************************************'
			print e
			print '********************************************'
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/ARC/BH_SAC'
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
			BH_raw_file.append(Address_events + '/' + events[l]['event_id'] + '/ARC/BH_RAW/' + \
				input_sta[i][0] + '.' + input_sta[i][1] + '.' + input_sta[i][2] + '.' + input_sta[i][3]) 
		
		for k in range(0, len(BH_raw_file)):
			
			print '********************************************'
			print str(k+1) + '/' + str(len(BH_raw_file))
			
			tr_tmp = read(BH_raw_file[k])
			tr = tr_tmp[0]
	
			resp_file = Address_events + '/' + events[l]['event_id'] + '/ARC/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print 'Response file:'
			print resp_file
			
			i1 = BH_raw_file[k][0]
			i2 = resp_file
			i3 = Address_events + '/' + events[l]['event_id']
			i4 = BH_raw_file[k][0] + '.' + BH_raw_file[k][1] + '.' + BH_raw_file[k][2] + '.' + BH_raw_file[k][3]
			commands.getoutput('./DMT_SAC.sh' + ' ' + i1 + ' ' + i2 + ' ' + i3 + ' ' + i4)
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

#########################################################################################################################
#########################################################################################################################
#########################################################################################################################

if __name__ == "__main__":
	status = DMT_SAC()
	#sys.exit(status)
