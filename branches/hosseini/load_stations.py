"""
Load stations from the directory
get the Lats, Lons and names of each
"""

import pickle
import glob
from obspy.core import read

def load_stations(Lon, Lat, name, Len_Lat_Lon, Num_Event, Address, Period):
	
	lons_sta = []
	lats_sta = []
	names_sta = []
	
	temp = 0
	
	for i in range(0, Num_Event):
		for j in range(0, Len_Lat_Lon[i]):
			lons_sta.append(Lon[j + temp][1])
			lats_sta.append(Lat[j + temp][1])
			names_sta.append(name[j + temp][1])
		temp = Len_Lat_Lon[i]
			
	return lons_sta, lats_sta, names_sta
	
'''
# ------------------------Trash-----------------------------
	
List_Stations = glob.glob(Address + '/Data/' + Period + '/' + events[Num_Event]['event_id'] + '/Arc_BH/*')
	
"""----------------------------------------------------------
Event_file = open(Address + '/Data/' + Period + '/list_event', 'r')
events = pickle.load(Event_file)
		
lat_event = []
lon_event = []
name_event = []
	
lat_event.append(events[Num_Event]['latitude'])
lon_event.append(events[Num_Event]['longitude'])
name_event.append(str(events[Num_Event]['depth']))
return lat_event, lon_event, name_event"""
'''
