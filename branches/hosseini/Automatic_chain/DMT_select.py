# ------------------------Import required Modules (Python and Obspy)-------------

"""
Required Python and Obspy modules will be imported in this part.
"""

from obspy.taup.taup import getTravelTimes, locations2degrees
from obspy.core import read

import pickle
import ConfigParser
import os
import sys

"""
Required Clients from Obspy will be imported and initialized here.
Please note that clients could be initialized other times within the program.
"""
from obspy.iris import Client as Client_iris

client_iris = Client_iris()


def DMT_select():
	
	# ------------------------Read INPUT file (Parameters)--------------------
	(input) = read_input()
	
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

###################################################### IRIS ######################################################

def IRIS(input):
	
	"""
	Call "IRIS_select" function based on your channel request.
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
	

###################################################### IRIS_select ######################################################

def IRIS_select(input, channel, interactive):
	
	phase = input['phase']
	freq = input['freq']

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
		select = open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/' + name_select, 'w')
		select.close()

		address = Address_events + '/' + events[l]['event_id'] + '/'
		input_file = open(address + 'IRIS/info/iris_' + channel)

		inp = input_file.readlines()

		for i in range(0, len(inp)):
			inp[i] = inp[i].split(',')
			if inp[i][2] == '  ':
				inp[i][2] = ''

		file = []

		for i in range(0, len(inp)):
			print '***************************************'
			print str(i) + '/' + str(len(inp)) 
			print inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3] + ' -- check '
			print '-----------------------'
			
			#dist = client_iris.distaz(stalat = float(inp[i][4]), stalon = float(inp[i][5]), evtlat = float(inp[i][9]), evtlon = float(inp[i][10]))
			#print 'iris'
			#print dist['distance']
			
			dist = locations2degrees(lat1 = float(inp[i][4]), long1 = float(inp[i][5]), lat2 = float(inp[i][9]), long2 = float(inp[i][10]))
			
			tt = getTravelTimes(delta=dist, depth=float(inp[i][11]), model=input['model'])
			
			for k in range(0, len(tt)):
				if tt[k]['phase_name'] in phase:
					try:
						
						print 'This station has ' + tt[k]['phase_name'] + ' phase...'
						
						st = read(address + 'IRIS/BH/' + inp[i][0] + '.' + inp[i][1] + '.' + inp[i][2] + '.' + inp[i][3])
						st[0].downsample(int(round(st[0].stats['sampling_rate'])/freq), no_filter=False)
						
						if st[0].stats['sampling_rate'] != 10.0:
							print inp[i][1]
							print st[0].stats['sampling_rate']
							print '------------------------------------------'
					
						num_evt = round((events[0]['datetime'] - st[0].stats['starttime'])*st[0].stats['sampling_rate'])
						num_pha = num_evt + round(tt[k]['time']*st[0].stats['sampling_rate'])
						
						select = open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/' + name_select, 'a')
						
						ph_info = tt[k]['phase_name'] + ',' + str(dist) + ',' + str(tt[k]['time']) + ',' + str(st[0].stats['sampling_rate']) + ',' + \
							str(num_evt) + ',' + str(num_pha) + ',' + inp[i][0] + ',' + inp[i][1] + ',' + inp[i][2] + ',' + inp[i][3] + ',' + \
							inp[i][4] + ',' + inp[i][5] + ',' + inp[i][6] + ',' + inp[i][7] + ',' + inp[i][8] + ',' + inp[i][9] + ',' + inp[i][10] + ',' + \
							inp[i][11] + ',' + inp[i][12] + ',' + '\n'
						
						select.writelines(ph_info)
						select.close()
					
					except Exception, e:
						print e
			
			print 'DONE'

#########################################################################################################################
#########################################################################################################################
#########################################################################################################################

if __name__ == "__main__":
	status = DMT_select()
	#sys.exit(status)
