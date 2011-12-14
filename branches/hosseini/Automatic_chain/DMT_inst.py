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
	This scrips uses 'seisSim' from obspy.signal for this reason
	
	Instrument Correction has three main steps:
		1) RTR: remove the trend
		2) tapering
		3) pre-filtering and deconvolution of Resp file from Raw counts
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
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_' + input['corr_unit'])
			
		except Exception, e:
			print '********************************************'
			print e
			print '********************************************'
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_' + input['corr_unit']
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
			
			rt_c = RTR(stream = BH_raw_file[k], degree = 2)
			
			tr_tmp = read(BH_raw_file[k])
			tr = tr_tmp[0]
			tr.data = rt_c
			
			# Tapering
			taper = invsim.cosTaper(len(tr.data))
			tr.data *= taper
			'''		
			if tr.stats['location'] == '':
				location = '--'
				resp_file = Address_events + '/' + events[l]['event_id'] + '/IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel']
			else:
			'''
			resp_file = Address_events + '/' + events[l]['event_id'] + '/IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print 'Response file:'
			print resp_file
			
			inst_corr(trace = tr, resp_file = resp_file, Address = Address_events + '/' + events[l]['event_id'] + '/IRIS/BH_' + input['corr_unit'] + '/', \
				unit = input['corr_unit'], BP_filter = input['pre_filt'])
	
	t_inst_2 = datetime.now()
	
	print '*********************************************************************'
	print 'Time passed for Instrument Correction of ' + channel + ' :'
	print t_inst_2 - t_inst_1
	print '*********************************************************************'

###################################################### inst_ARC ######################################################

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
	This scrips uses 'seisSim' from obspy.signal for this reason
	
	Instrument Correction has three main steps:
		1) RTR: remove the trend
		2) tapering
		3) pre-filtering and deconvolution of Resp file from Raw counts
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
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/ARC/BH_' + input['corr_unit'])
			
		except Exception, e:
			print '********************************************'
			print e
			print '********************************************'
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/ARC/BH_' + input['corr_unit']
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
			
			rt_c = RTR(stream = BH_raw_file[k], degree = 2)
			
			tr_tmp = read(BH_raw_file[k])
			tr = tr_tmp[0]
			tr.data = rt_c
			
			# Tapering
			taper = invsim.cosTaper(len(tr.data))
			tr.data *= taper
			'''		
			if tr.stats['location'] == '--':
				location = ''
				resp_file = Address_events + '/' + events[l]['event_id'] + '/ARC/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel']
			else:
			'''
			resp_file = Address_events + '/' + events[l]['event_id'] + '/ARC/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print 'Response file:'
			print resp_file
			
			inst_corr(trace = tr, resp_file = resp_file, Address = Address_events + '/' + events[l]['event_id'] + '/ARC/BH_' + input['corr_unit'] + '/', \
				unit = input['corr_unit'], BP_filter = input['pre_filt'])
	
	t_inst_2 = datetime.now()
	
	print '*********************************************************************'
	print 'Time passed for Instrument Correction of ' + channel + ' :'
	print t_inst_2 - t_inst_1
	print '*********************************************************************'
	
###################################################### RTR ######################################################

def RTR(stream, degree = 2):
	
	"""
	Remove the trend by	Fitting a linear function to the trace with least squares and subtracting it
	"""
	
	raw_f = read(stream)

	t = []
	b0 = 0
	inc = []
	
	b = raw_f[0].stats['starttime']

	for i in range(0, raw_f[0].stats['npts']):
		inc.append(b0)
		b0 = b0+1.0/raw_f[0].stats['sampling_rate'] 
		b0 = round(b0, 4)
		
	A = np.vander(inc, degree)
	(coeffs, residuals, rank, sing_vals) = np.linalg.lstsq(A, raw_f[0].data)
	'''
	print '--------------------'
	print 'coeffs = ' + str(coeffs)
	print 'residuals = ' + str(residuals)
	print 'rank = ' + str(rank)
	print 'sing_vals = ' + str(sing_vals)
	print '--------------------'
	'''
	f = np.poly1d(coeffs)
	y_est = f(inc)
	rt_c = raw_f[0].data-y_est
	
	return rt_c

###################################################### inst_corr ######################################################

def inst_corr(trace, resp_file, Address, unit = 'DIS', BP_filter = (0.008, 0.012, 3.0, 4.0)):

	date = trace.stats['starttime']
	seedresp = {'filename':resp_file,'date':date,'units':unit}
	
	try:
		
		trace.data = seisSim(data = trace.data,samp_rate = trace.stats.sampling_rate,paz_remove=None, \
			paz_simulate = None, remove_sensitivity=False, simulate_sensitivity = False, water_level = 600.0, \
			zero_mean = True, taper = False, pre_filt=BP_filter, seedresp=seedresp)
		'''
		if trace.stats['location'] == '':
			location = '--'
			trace.write(Address + \
				trace.stats['network'] + '.' + trace.stats['station'] + '.' + location + \
				'.' + trace.stats['channel'], format = 'SAC')
				
		else:
		'''
		trace.write(Address + \
				trace.stats['network'] + '.' + trace.stats['station'] + '.' + trace.stats['location'] + \
				'.' + trace.stats['channel'], format = 'SAC')
		
		print '-----------------------'
		print 'Instrument Correction for ' + trace.stats['network'] + '.' + trace.stats['station'] + '.' + trace.stats['location'] + \
				'.' + trace.stats['channel'] + ' is done!'
		
	except Exception, e:
		print e

#########################################################################################################################
#########################################################################################################################
#########################################################################################################################

if __name__ == "__main__":
	status = DMT_inst()
	#sys.exit(status)
