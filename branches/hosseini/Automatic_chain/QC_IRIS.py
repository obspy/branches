from obspy.mseed.libmseed import LibMSEED
from obspy.core import read
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pickle
import shutil


def QC_IRIS(input):
	
	'''
	Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
	Address_events = input['Address'] + '/Data/' + Period
	'''
	
	Address_data = input['Address'] + '/Data_TEST3'
	ls_period = os.listdir(Address_data)
	
	pre_ls_event = []
	for i in range(0, len(ls_period)):
		pre_ls_event.append(Address_data + '/' + ls_period[i])
	
	
	ls_event_file = []
	for i in pre_ls_event:
		ls_event_file.append(os.listdir(i))
	
	ls_event = []
	
	for i in range(0, len(ls_event_file)):
		for j in range(0, len(ls_event_file[i])):
			if ls_event_file[i][j] == 'list_event':
				print ' '
			else:
				ls_event.append(Address_data + '/' + ls_period[i] + '/' + ls_event_file[i][j])
				print ls_event_file[i][j]
	
	add_IRIS_QC = []
	
	for i in ls_event:
		add_IRIS_QC.append(i + '/IRIS/QC')
		
	add_IRIS_events = []
	for i in pre_ls_event:
		add_IRIS_events.append(i + '/list_event')
		
	events_all = []
	
	for i in add_IRIS_events:
		Event_file = open(i, 'r')
		events_all.append(Event_file)
			
	for l in range(0, len(events_all)):
		
		events = pickle.load(events_all[l])
		len_events = len(events)
		#import ipdb; ipdb.set_trace()
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
			
			List_IRIS_BHE.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHE'))
			List_IRIS_BHN.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHN'))
			List_IRIS_BHZ.append(glob.glob(pre_ls_event[l] + '/' + events[k]['event_id'] + '/IRIS/' + '*.BHZ'))

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
				if gap_BHE[i] == []:
					print 'GAP -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				
				else:
					gap_prob_BHE.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))
			
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
						events[k]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHE[i][0] + \
						'.' + Sta_BHE[i][1] + '.' + Sta_BHE[i][2] + '.' + 'BHE' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e

				
			TQ_prob_BHE = []
			
			for i in range(0, len(TQ_BHE)):
				if TQ_BHE[i] == {}:
					print 'TQ -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				else:
					TQ_prob_BHE.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))


			
			TIME_str = []
			#import ipdb; ipdb.set_trace()
			
			if len(TQ_prob_BHE) == 0:
				TIME_str.append('None')
			
			else:
				for i in TQ_prob_BHE:
					#import ipdb; ipdb.set_trace()
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
				if gap_BHN[i] == []:
					print 'GAP -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				
				else:
					gap_prob_BHN.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))
			
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
						events[k]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHN[i][0] + \
						'.' + Sta_BHN[i][1] + '.' + Sta_BHN[i][2] + '.' + 'BHN' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
			
				
			TQ_prob_BHN = []
			
			for i in range(0, len(TQ_BHN)):
				if TQ_BHN[i] == {}:
					print 'TQ -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				else:
					TQ_prob_BHN.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))


			
			TIME_str = []
			#import ipdb; ipdb.set_trace()
			
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
				if gap_BHZ[i] == []:
					print 'GAP -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				
				else:
					gap_prob_BHZ.append(i)
					print 'GAP -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))
			
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
						events[k]['event_id'] + '/IRIS/EXCEP/' + 'Exception_file_IRIS', 'a')

					ee = 'TQ-DQ' + '---' + str(k) + '-' + str(i) + '---' + Sta_BHZ[i][0] + \
						'.' + Sta_BHZ[i][1] + '.' + Sta_BHZ[i][2] + '.' + 'BHZ' + \
						'---' + str(e) + '\n'
						
					Exception_file.writelines(ee)
					Exception_file.close()
					print e
				
				
			TQ_prob_BHZ = []
			
			for i in range(0, len(TQ_BHZ)):
				if TQ_BHZ[i] == {}:
					print 'TQ -- Done' + ' -- ' + str(l+1) + '/' + str(len(events_all))
				else:
					TQ_prob_BHZ.append(i)
					print 'TQ -- ' + str(i) + ' -- ' + str(l+1) + '/' + str(len(events_all))


			
			TIME_str = []
			#import ipdb; ipdb.set_trace()
			
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
