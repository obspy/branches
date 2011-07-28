from obspy.mseed.libmseed import LibMSEED
from obspy.core import read
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pickle
import shutil


def QC_ARC(input):
	
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/Data/' + Period
	
	Event_file = open(Address_events + '/list_event', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)

	for k in range(0, len_events):
		
			if os.path.exists(Address_events + '/' + events[k]['event_id'] + '/ARC/QC/') == 'True':
				
				shutil.rmtree(Address_events + '/' + events[k]['event_id'] + '/ARC/QC/')
				os.makedirs(Address_events + '/' + events[k]['event_id'] + '/ARC/QC/')
			
			else:
				os.makedirs(Address_events + '/' + events[k]['event_id'] + '/ARC/QC/')			
			

	for k in range(0, len_events):
		gapfile = open(Address_events + '/' + events[k]['event_id'] + \
			'/ARC/QC/' + 'GAP', 'w')
		eventsID = events[k]['event_id']
		gapfile.writelines('\n' + eventsID + '\n')
		gapfile.writelines('----------------------------ARC----------------------------'+ '\n')
		gapfile.writelines('----------------------------GAP----------------------------'+ '\n')
		gapfile.close()
		
		timefile = open(Address_events + '/' + events[k]['event_id'] + \
			'/ARC/QC/' + 'TimingQuality', 'w')
		eventsID = events[k]['event_id']
		timefile.writelines('\n' + eventsID + '\n')
		timefile.writelines('----------------------------ARC----------------------------'+ '\n')
		timefile.writelines('----------------------------TIMEQ----------------------------'+ '\n')
		timefile.close()
		
		datafile = open(Address_events + '/' + events[k]['event_id'] + \
			'/ARC/QC/' + 'DataQuality', 'w')
		eventsID = events[k]['event_id']
		datafile.writelines('\n' + eventsID + '\n')
		datafile.writelines('----------------------------ARC----------------------------'+ '\n')
		datafile.writelines('----------------------------DATAQ----------------------------'+ '\n')
		datafile.close()
	
	
	List_ARC_BHE = []
	List_ARC_BHN = []
	List_ARC_BHZ = []
	
	
	for k in range(0, len_events):
		
		List_ARC_BHE.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/ARC/' + '*.BHE'))
		List_ARC_BHN.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/ARC/' + '*.BHN'))
		List_ARC_BHZ.append(glob.glob(Address_events + '/' + events[k]['event_id'] + '/ARC/' + '*.BHZ'))

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
			if gap_BHE[i] == []:
				print 'Done'
			
			else:
				gap_prob_BHE.append(i)
				print i
		
		GAP_str = []
		
		if len(gap_prob_BHE) == 0:
			GAP_str.append('None')
		
		else:
			for i in gap_prob_BHE:
				gap_str = str(i) + '  ' + gap_BHE[i][0][0] + '  ' + gap_BHE[i][0][1] + '  ' + \
					gap_BHE[i][0][2] + '  ' + gap_BHE[i][0][3] + '  ' + str(len(gap_BHE[i])) + '\n'
				GAP_str.append(gap_str)
			
		
		gapfile = open(Address_events + '/' + events[k]['event_id'] + \
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
					
				Exception_file = open(Address_events + '/' + \
					events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

				ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHE[i][0] + \
					'.' + Sta_BHE[i][1] + '.' + Sta_BHE[i][2] + '.' + 'BHE' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
			
			
		TQ_prob_BHE = []
		
		for i in range(0, len(TQ_BHE)):
			if TQ_BHE[i] == {}:
				print 'Done'
			else:
				TQ_prob_BHE.append(i)
				print i


		
		TIME_str = []
		#import ipdb; ipdb.set_trace()
		
		if len(TQ_prob_BHE) == 0:
			TIME_str.append('None')
		
		else:
			for i in TQ_prob_BHE:
				time_str = str(i) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
					Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '\n'
				TIME_str.append(time_str)
			
		
		timefile = open(Address_events + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'TimingQuality', 'a')
		timefile.writelines(TIME_str)
		timefile.writelines('\n')
		timefile.close()
		
		
		
		DATA_str = []
		
		for i in range(0, len(DQ_BHE)):
			data_str = str(i) + '  ' + str(DQ_BHE[i]) + '  ' + Sta_BHE[i][0] + '  ' + Sta_BHE[i][1] + '  ' + \
				Sta_BHE[i][2] + '  ' + Sta_BHE[i][3] + '\n'
			DATA_str.append(data_str)
		
		
		datafile = open(Address_events + '/' + events[k]['event_id'] + \
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
			if gap_BHN[i] == []:
				print 'Done'
			
			else:
				gap_prob_BHN.append(i)
				print i
		
		GAP_str = []
		
		if len(gap_prob_BHN) == 0:
			GAP_str.append('None')
		
		else:
			for i in gap_prob_BHN:
				gap_str = str(i) + '  ' + gap_BHN[i][0][0] + '  ' + gap_BHN[i][0][1] + '  ' + \
					gap_BHN[i][0][2] + '  ' + gap_BHN[i][0][3] + '  ' + str(len(gap_BHN[i])) + '\n'
				GAP_str.append(gap_str)
			
		
		gapfile = open(Address_events + '/' + events[k]['event_id'] + \
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
					
				Exception_file = open(Address_events + '/' + \
					events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

				ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHN[i][0] + \
					'.' + Sta_BHN[i][1] + '.' + Sta_BHN[i][2] + '.' + 'BHN' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
			
		TQ_prob_BHN = []
		
		for i in range(0, len(TQ_BHN)):
			if TQ_BHN[i] == {}:
				print 'Done'
			else:
				TQ_prob_BHN.append(i)
				print i


		
		TIME_str = []
		#import ipdb; ipdb.set_trace()
		
		if len(TQ_prob_BHN) == 0:
			TIME_str.append('None')
		
		else:
			for i in TQ_prob_BHN:
				time_str = str(i) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
					Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '\n'
				TIME_str.append(time_str)
			
		
		timefile = open(Address_events + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'TimingQuality', 'a')
		timefile.writelines(TIME_str)
		timefile.writelines('\n')
		timefile.close()
		
		
		
		DATA_str = []
		
		for i in range(0, len(DQ_BHN)):
			data_str = str(i) + '  ' + str(DQ_BHN[i]) + '  ' + Sta_BHN[i][0] + '  ' + Sta_BHN[i][1] + '  ' + \
				Sta_BHN[i][2] + '  ' + Sta_BHN[i][3] + '\n'
			DATA_str.append(data_str)
		
		
		datafile = open(Address_events + '/' + events[k]['event_id'] + \
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
			if gap_BHZ[i] == []:
				print 'Done'
			
			else:
				gap_prob_BHZ.append(i)
				print i
		
		GAP_str = []
		
		if len(gap_prob_BHZ) == 0:
			GAP_str.append('None')
		
		else:
			for i in gap_prob_BHZ:
				gap_str = str(i) + '  ' + gap_BHZ[i][0][0] + '  ' + gap_BHZ[i][0][1] + '  ' + \
					gap_BHZ[i][0][2] + '  ' + gap_BHZ[i][0][3] + '  ' + str(len(gap_BHZ[i])) + '\n'
				GAP_str.append(gap_str)
			
		
		gapfile = open(Address_events + '/' + events[k]['event_id'] + \
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
					
				Exception_file = open(Address_events + '/' + \
					events[i]['event_id'] + '/ARC/EXCEP/' + 'Exception_file_ARC', 'a')

				ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHZ[i][0] + \
					'.' + Sta_BHZ[i][1] + '.' + Sta_BHZ[i][2] + '.' + 'BHZ' + \
					'---' + str(e) + '\n'
					
				Exception_file.writelines(ee)
				Exception_file.close()
				print e
			
			
		TQ_prob_BHZ = []
		
		for i in range(0, len(TQ_BHZ)):
			if TQ_BHZ[i] == {}:
				print 'Done'
			else:
				TQ_prob_BHZ.append(i)
				print i


		
		TIME_str = []
		#import ipdb; ipdb.set_trace()
		
		if len(TQ_prob_BHZ) == 0:
			TIME_str.append('None')
		
		else:
			for i in TQ_prob_BHZ:
				time_str = str(i) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
					Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '\n'
				TIME_str.append(time_str)
			
		
		timefile = open(Address_events + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'TimingQuality', 'a')
		timefile.writelines(TIME_str)
		timefile.writelines('\n')
		timefile.close()
		
		
		
		DATA_str = []
		
		for i in range(0, len(DQ_BHZ)):
			data_str = str(i) + '  ' + str(DQ_BHZ[i]) + '  ' + Sta_BHZ[i][0] + '  ' + Sta_BHZ[i][1] + '  ' + \
				Sta_BHZ[i][2] + '  ' + Sta_BHZ[i][3] + '\n'
			DATA_str.append(data_str)
		
		
		datafile = open(Address_events + '/' + events[k]['event_id'] + \
				'/ARC/QC/' + 'DataQuality', 'a')
		datafile.writelines(DATA_str)
		datafile.writelines('\n')
		datafile.close()
