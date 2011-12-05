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
		
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()
	import ipdb; ipdb.set_trace()
	IRIS(input)

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
	
###################################################### update_req_sta_IRIS ######################################################
	
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
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/IRIS/BH')
			
		except Exception, e:
			print '********************************************'
			print e
			print '********************************************'
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/IRIS/BH'
			print "exists in your directory..."
			print 'The program will continue in the same folder!'
			
		input_sta = input_file[l].readlines()
		
		for i in range(0, len(input_sta)):
			input_sta[i] = input_sta[i].split(',')
		
		BH_raw_file = []
		resp_file = []

		for i in range(0, len(input_sta)):
			if input_sta[i][2] == '  ':
				input_sta[i][2] = '--'
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
						
			if tr.stats['location'] == '':
				location = '--'
				resp_file = Address_events + '/' + events[l]['event_id'] + '/IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel']
			else:
				resp_file = Address_events + '/' + events[l]['event_id'] + '/IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print 'Response file:'
			print resp_file
			
			inst_corr(trace = tr, resp_file = resp_file, Address = Address_events + '/' + events[l]['event_id'] + '/IRIS/BH/', \
				unit = input['corr_unit'], BP_filter = input['pre_filt'])
	
	t_inst_2 = datetime.now()
	
	print '*********************************************************************'
	print 'Time passed for Instrument Correction of ' + channel + ' :'
	print t_inst_2 - t_inst_1
	print '*********************************************************************'

###################################################### RTR ######################################################

def RTR(stream, degree = 2):
	
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
		
		if trace.stats['location'] == '':
			location = '--'
			trace.write(Address + \
				trace.stats['network'] + '.' + trace.stats['station'] + '.' + location + \
				'.' + trace.stats['channel'], format = 'SAC')
				
		else:
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
	sys.exit(status)
