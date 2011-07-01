#!!!!! CHECK!!!! network and stations and channels!!!!
"""
Return the available IRIS stations at the IRIS-DMC for all requested events
"""

from obspy.iris import Client as Client_iris
from obspy.core import UTCDateTime
from datetime import datetime
import time
import os
from lxml import objectify, etree

client_iris = Client_iris()

def IRIS_get_Network_XML(len_events, events, Address_events, net, sta, loc, cha, lat_cba, lon_cba, mr_cba, \
		Mr_cba, mlat_rbb, Mlat_rbb, mlon_rbb, Mlon_rbb)
		
	t_iris_1 = datetime.now()
	
	t = []
	
	dic = {}
	dic_target = {}
	
	for i in range(0, len_events):
		t.append(UTCDateTime(events[i]['datetime']))
		dic[i] = {}
		
		while True:
			try:
				Result = client_iris.availability(net, sta, loc, cha, t[i]-10, t[i]+10,lat_cba, lon_cba, mr_cba, \
					Mr_cba, mlat_rbb, Mlat_rbb, mlon_rbb, Mlon_rbb, output='xml')
				 #minlat = 20, maxlat = 50, minlon = -124, maxlon = -70, output='xml')
				xml_doc = etree.fromstring(Result)
				xml_doc_string = etree.tostring(xml_doc)
				num_station = xml_doc_string.count('/Station')

				j=0
				
				for k in range(0, num_station):
					#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
					#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
					Sta_net_code = xml_doc.xpath('/StaMessage/Station')[k].get('net_code')
					Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[k].get('sta_code')
					Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[k].text
					Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[k].text
					#Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[i].text
					Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[k].get('loc_code')
					Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[k].get('chan_code')
					#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
					#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
					#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + \
					#Sta_chan_code + '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + \
					#Sta_End_time, 'Network': Sta_net_code, 'Station': Sta_sta_code, \
					#'Start_time': Sta_Start_time, 'End_time': Sta_End_time, \
					#'Latitude': Sta_Lat, 'Longitude': Sta_Lon, 'Elevation': Sta_Elevation, \
					#'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
					dic[i][str(k)] ={'Info': Sta_net_code + '--' + Sta_sta_code, 'Network': Sta_net_code, \
						'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
						'Location': Sta_loc_code, 'Channel': Sta_chan_code}
				break

			except Exception, e:
				print e
			
	#CHECK!
	#for the first Event!!!
	#len_req_iris_BH = len(dic)
		
	for i in range(0, len_events):
		#import os
		#folder = os.path.join(Address, 'Data', Period, events[i]['event_id'])
		os.makedirs(Address_events + '/' + events[i]['event_id'])
		os.makedirs(Address_events + '/' + events[i]['event_id'] + '/IRIS')

	print 'Folders are Created!'

	t_iris_2 = datetime.now()
	t_iris = t_iris_2 - t_iris_1
	
	print 'IRIS-Time: (Availability)'
	print t_iris
	
	
	
	#CHECK!
	#print 'length of required IRIS channels:'
	#print len_req_iris_BH
	
	return dic, t

'''
# ------------------------Target Dics---------------------------------	
	dic = {}
	dic_target = {}

	j=0
	
	for i in range(0, num_station):
		#Sta_source = xml_doc.xpath('/StaMessage/Source')[0].text
		#Sta_SentDate = xml_doc.xpath('/StaMessage/SentDate')[0].text
		Sta_net_code = xml_doc.xpath('/StaMessage/Station')[i].get('net_code')
		Sta_sta_code = xml_doc.xpath('/StaMessage/Station')[i].get('sta_code')
		Sta_Lat = xml_doc.xpath('/StaMessage/Station/Lat')[i].text
		Sta_Lon = xml_doc.xpath('/StaMessage/Station/Lon')[i].text
		#Sta_Elevation = xml_doc.xpath('/StaMessage/Station/Elevation')[i].text
		Sta_loc_code = xml_doc.xpath('/StaMessage/Station/Channel')[i].get('loc_code')
		Sta_chan_code = xml_doc.xpath('/StaMessage/Station/Channel')[i].get('chan_code')
		#Sta_Start_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('start')
		#Sta_End_time = xml_doc.xpath('/StaMessage/Station/Channel/Availability/Extent')[i].get('end')
		#dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code + '--' + Sta_chan_code \
			+ '--' + Sta_loc_code + '--' + Sta_Start_time + '--' + Sta_End_time, \
			'Network': Sta_net_code, 'Station': Sta_sta_code, 'Start_time': Sta_Start_time, \
			'End_time': Sta_End_time, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
			'Elevation': Sta_Elevation, 'Location_code': Sta_loc_code, 'Channel_code': Sta_chan_code}
		dic[i] ={'Info': Sta_net_code + '--' + Sta_sta_code, 'Network': Sta_net_code, \
			'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon, \
			'Location': Sta_loc_code, 'Channel': Sta_chan_code}
	
		#if float(dic[i]['Latitude']) <= 40 and float(dic[i]['Longitude']) <= -110:
			#dic_target[j] ={'Info': Sta_net_code + '--' + Sta_sta_code, \
			'Network': Sta_net_code, 'Station': Sta_sta_code, 'Latitude': Sta_Lat, 'Longitude': Sta_Lon}
		#j += 1
	"""
	for i in range(0, num_station):
		print dic[i]['Latitude']
	"""
	print '--------------------------------------------'
	print j
	for k in range(0, j):
		print dic_target[k]
'''
