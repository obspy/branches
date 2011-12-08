# ------------------------Import required Modules (Python and Obspy)-------------

"""
Required Python and Obspy modules will be imported in this part.
"""

from obspy.core import read

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
import ConfigParser
import os
import sys
import pickle

def DMT_TF():
	
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()
	
	(trace_all) = IRIS(input)
	


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
	
	input['TF_phase'] = config.get('TF_chips', 'TF_phase')
	input['np_before'] = config.getint('TF_chips', 'np_before')
	input['np_all'] = config.getint('TF_chips', 'np_all')
	input['SNR_YN'] = config.get('TF_chips', 'SNR_YN')
	input['SNR_limit'] = config.getfloat('TF_chips', 'SNR_limit')
	
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

###################################################### IRIS ######################################################

def IRIS(input):
	
	"""
	Call "IRIS_TF" function based on your channel request.
	"""

	if input['BHE'] == 'Y':
		IRIS_select(input, channel = 'BHE', interactive = input['inter_address'])
	
	if input['BHN'] == 'Y':
		IRIS_select(input, channel = 'BHN', interactive = input['inter_address'])
	
	if input['BHZ'] == 'Y':
		IRIS_select(input, channel = 'BHZ', interactive = input['inter_address'])

	print "-------------------------------------------------"
	print 'Select seismograms from IRIS is DONE'
	print "-------------------------------------------------"
	

def IRIS_select(input, channel, interactive):
	plt.clf()
	plt.ion()
	
	phase = input['phase']
	freq = input['freq']
	
	np_before = input['np_before']
	np_all = input['np_all']
	
	name_select = phase[0]

	if len(phase) > 1:
		for i in range(1, len(phase)):
			name_select += '_' + phase[i]

	name_select += '_' + channel + '.dat' 
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter
	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	for l in range(0, len_events):
		select = open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/' + name_select, 'r')

		ph_file = select.readlines()

		for i in range(0, len(ph_file)):
			ph_file[i] = ph_file[i].split(',')
			
		address = Address_events + '/' + events[l]['event_id'] + '/'

		trace_all = []

		for i in range(0, len(ph_file)):

			if ph_file[i][0] == input['TF_phase'] and float(ph_file[i][1]) >90 and float(ph_file[i][1]) < 115:
				
				st = read(address + 'IRIS/BH/' + ph_file[i][6] + '.' + ph_file[i][7] + '.' + ph_file[i][8] + '.' + ph_file[i][9])
				#st1 = read(address + 'IRIS/sac_folder/' + ph_file[i][6] + '.' + ph_file[i][7] + '.' + ph_file[i][8] + '.' + ph_file[i][9])
				st[0].downsample(int(round(st[0].stats['sampling_rate'])/freq), no_filter=False)
				#st1[0].downsample(int(round(st1[0].stats['sampling_rate'])/freq), no_filter=False)
						
				trace = st[0]
				#st1[0].data /= 1e6
				st[0].data *= 1e3
				
				#print st[0].max()
				'''
				if  68.5 < (st[0].data[0] + float(ph_file[i][1])) < 68.9:
					print st[0].stats['network']
					print st[0].stats['station']
					print st[0].stats['location']
				'''
				
				if -8 < st[0].max() < 8:
				#if -8 < st[0].max() < 8 and -8 < st1[0].max() < 8:
					st[0].data += float(ph_file[i][1])
					#st1[0].data += float(ph_file[i][1])
					'''
					plt.plot(range(0, len(st[0].data)), st[0].data, 'red')
					plt.plot(range(0, len(st1[0].data)), st1[0].data, 'black')
					'''
				
				trace.data = trace.data[(int(float(ph_file[i][5]))-np_before):((int(float(ph_file[i][5]))-np_before)+np_all)]
				trace.stats['starttime'] += (float(ph_file[i][5])-np_before)/trace.stats['sampling_rate']
				trace_all.append(trace)
				
				# NICE!
				#time_plt = np.linspace((float(ph_file[i][4]))/trace.stats['sampling_rate'], ((float(ph_file[i][4]))+1024)/trace.stats['sampling_rate'], trace.stats['npts'])
				time_plt = np.linspace((float(ph_file[i][5])-float(ph_file[i][4])-np_before)/trace.stats['sampling_rate'], ((float(ph_file[i][5])-float(ph_file[i][4])-np_before)+np_all)/trace.stats['sampling_rate'], trace.stats['npts'])
				p1 = trace.data[0:np_before]; p1 = p1**2; p1 = p1.sum(); p1 = p1/len(trace.data[0:np_before]); p1 = sqrt(p1)
				p2 = trace.data[(np_before + 1):np_all]; p2 = p2**2; p2 = p2.sum(); p2 = p2/len(trace.data[(np_before + 1):np_all]); p2 = sqrt(p2)
				
				try:
					print max(trace.data)
					if max(trace.data) < 200:
						if p2/p1 > input['SNR_limit']:	
							print 'zero:'
							print trace.data[0]
							trace.detrend(type='simple')
							plt.plot(time_plt, (trace.data - trace.data[0]) * 5 + trace.data[0] + float(ph_file[i][1]), 'black')
							#plt.plot(trig_all[i][0][0]/trace.stats['sampling_rate'], float(ph_file[i][1]), 'o')
				except Exception, e:
					print e
	
	trace_file = open('/home/kasra/Desktop/trace_all', 'w')
	pickle.dump(trace_all, trace_file)
	trace_file.close()
	
	plt.savefig('/home/kasra/Desktop/pic.pdf')
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################

if __name__ == "__main__":
	status = DMT_TF()
	#sys.exit(status)
