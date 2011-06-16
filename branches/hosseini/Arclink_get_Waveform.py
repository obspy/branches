"""
ATTENTION: 
In "client_arclink.saveWaveform" we save each channel (BHE, BHN and BHZ) 
seperately. It has one advantage: we have all of the waveforms in seperate files
BUT it has a disadvantage...if the Internet connection encounters any problem
in the middle...!!!! so maybe it is better to change the code for all available
channels BH*...and then split them into different BHE, N and Z
"""

"""
get Waveform from Arclink
get Lons and Lats of each station from Inventory (needed for plotting) 
"""

from obspy.arclink import Client as Client_arclink
from datetime import datetime
import time
from obspy.arclink.client import ArcLinkException as ArcLinkException

# client_arclink = Client_arclink(timeout = 30, command_delay=0.1)
client_arclink = Client_arclink()

def Arclink_get_Waveform(Address, Period, len_events, events, Nets_Arc_req_BHE, \
	Nets_Arc_req_BHN, Nets_Arc_req_BHZ, t, ArcLinkException):
	
	for i in range(0, len_events):
		Exception_file1 = open(Address + '/Data/' + Period + '/' + \
			events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_1', 'w')
		Exception_file2 = open(Address + '/Data/' + Period + '/' + \
			events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_1', 'w')
		Exception_file1.close()
		Exception_file2.close()
	
	t_wave_1 = datetime.now()
	
	Len_Lat_Lon = []
	Lat = []
	Lon = []
	name = []

	# client_arclink = Client_arclink(debug=True, timeout=10, command_delay=0.1)
	client_arclink = Client_arclink()
	
	for i in range(0, len_events):
		Lat_temp = []
		Lon_temp = []
		name_temp = []
		len_req_Arc_BHE = len(Nets_Arc_req_BHE[i]) 
		'''
		#for j in range(0, len_req_Arc_BHE):
		for j in range(11,20):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'Arclink-Event and Station Numbers are:'
			print EC + '-BHE'
			try:
				#time.sleep(2)
				#client_arclink = Client_arclink(debug=True)
				client_arclink = Client_arclink()
				
				client_arclink.saveWaveform(Address + '/Data/' + Period + \
					'/' + events[i]['event_id'] + '/Arc_BH/' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + str(Nets_Arc_req_BHE[i][j][2]) + '-' + \
					'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
					Nets_Arc_req_BHE[i][j][2], 'BHE', t[i]-300, t[i]+4800)
				
				client_arclink.close()
				
                
			# It is indeed crazy but we want to work with Hiccup (ask Robert)
			except ArcLinkException, e:	
				print Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1]
				
				Exception_file1 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_1', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHE' + '---' + str(e) + '\n'
				
				Exception_file1.writelines(ee)
				
				print e
				client_arclink.close()
			
			except Exception, e:
				Exception_file2 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_2', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' +  \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHE' + '---' + str(e) + '\n'
				
				Exception_file2.writelines(ee)
				
				print e
			
		#for j in range(0, len_req_Arc_BHE):
		for j in range(11,20):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'Arclink-Event and Station Numbers are:'
			print EC + '-BHN'
			try:
				#time.sleep(2)
				#client_arclink = Client_arclink(debug=True)
				client_arclink = Client_arclink()
		
				client_arclink.saveWaveform(Address + '/Data/' + Period + \
					'/' + events[i]['event_id'] + '/Arc_BH/' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + str(Nets_Arc_req_BHE[i][j][2]) + '-' + \
					'BHE', Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
					Nets_Arc_req_BHE[i][j][2], 'BHN', t[i]-300, t[i]+4800)
				
				client_arclink.close()
				
                
			# It is indeed crazy but we want to work with Hiccup (ask Robert)
			except ArcLinkException, e:	
				print Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1]
				
				Exception_file1 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_1', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHN' + '---' + str(e) + '\n'
				
				Exception_file1.writelines(ee)
				
				print e
				client_arclink.close()
			
			except Exception, e:
				Exception_file2 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_2', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' +  \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHN' + '---' + str(e) + '\n'
				
				Exception_file2.writelines(ee)
				
				print e
		'''
		#for j in range(0, len_req_Arc_BHE):
		for j in range(11,20):
			EC = str(i+1) + '-' + str(j)
			print '------------------'
			print 'Arclink-Event and Station Numbers are:'
			print EC + '-BHZ'
			try:
				#time.sleep(2)
				#client_arclink = Client_arclink(debug=True)
				client_arclink = Client_arclink()
				
				client_arclink.saveWaveform(Address + '/Data/' + Period + \
					'/' + events[i]['event_id'] + '/Arc_BH/' + str(Nets_Arc_req_BHZ[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHZ[i][j][1]) + '-' + str(Nets_Arc_req_BHZ[i][j][2]) + '-' + \
					'BHZ', Nets_Arc_req_BHZ[i][j][0], Nets_Arc_req_BHZ[i][j][1], \
					Nets_Arc_req_BHZ[i][j][2], 'BHZ', t[i]-300, t[i]+4800)
				
				client_arclink.saveResponse(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'RESP/' + \
					str(Nets_Arc_req_BHE[i][j][0]) + '-' + str(Nets_Arc_req_BHE[i][j][1]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BH', \
					Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1], \
					Nets_Arc_req_BHE[i][j][2], 'BH*', t[i]-300, t[i]+4800)
								
				#!!!! You could change this part with PARSER!!!!
				Inv = client_arclink.getInventory(Nets_Arc_req_BHE[i][j][0], \
					Nets_Arc_req_BHE[i][j][1], Nets_Arc_req_BHE[i][j][2], 'BH*')
				
				Lat_temp.append([i, Inv[Nets_Arc_req_BHE[i][j][0] + '.' + \
					Nets_Arc_req_BHE[i][j][1]]['latitude']])
				Lon_temp.append([i, Inv[Nets_Arc_req_BHE[i][j][0] + '.' + \
					Nets_Arc_req_BHE[i][j][1]]['longitude']])
				name_temp.append([i, Nets_Arc_req_BHE[i][j][0] + '.' + \
					Nets_Arc_req_BHE[i][j][1]])
				
				Lat.append([i, Inv[Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1]]['latitude']])
				Lon.append([i, Inv[Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1]]['longitude']])
				name.append([i, Nets_Arc_req_BHE[i][j][0] + '.' + Nets_Arc_req_BHE[i][j][1]])
				
				client_arclink.close()
				
                
			# It is indeed crazy but we want to work with Hiccup (ask Robert)
			except ArcLinkException, e:	
				print Nets_Arc_req_BHE[i][j][0], Nets_Arc_req_BHE[i][j][1]
				
				Exception_file1 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_1', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' + \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHZ' + '---' + str(e) + '\n'
				
				Exception_file1.writelines(ee)
				
				print e
				client_arclink.close()
			
			except Exception, e:
				Exception_file2 = open(Address + '/Data/' + Period + '/' + \
					events[i]['event_id'] + '/Arc_BH/' + 'Exception_file_Arc_2', 'a')
				
				ee = str(i) + str(j) + '-' + str(Nets_Arc_req_BHE[i][j][0]) + \
					'-' + str(Nets_Arc_req_BHE[i][j][1]) + '-' +  \
					str(Nets_Arc_req_BHE[i][j][2]) + '-' + 'BHZ' + '---' + str(e) + '\n'
				
				Exception_file2.writelines(ee)
				
				print e
				
		Len_Lat_Lon.append(len(Lat_temp)) 
	
	return Lat, Lon, name, Len_Lat_Lon
	
	print 'Arclink and BH* is DONE'

	t_wave_2 = datetime.now()
	t_wave = t_wave_2 - t_wave_1

	Exception_file1.close()
	Exception_file2.close()
	print "Time for getting Waveforms from Arclink:"
	print t_wave
