"""
Plot the ray path for each event to all available stations
"""

import pickle
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import ipdb

def ray_path(Address, Period, file_name, events, Ser_name, lon_event, lat_event, name_event, Num_Event, \
		lons_sta, lats_sta, names_sta):
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	#m = Basemap(projection='moll', lon_0=-100, lat_0=39, resolution='c')
	m = Basemap(projection='moll', lon_0=lon_event, lat_0=lat_event, resolution='c')
	
	# Different Options for drawing the Earth:
	#m = Basemap(projection='lcc',lon_0=0,resolution='c')
	#m.bluemarble()
	#m.drawcountries(linewidth=2)
	
	m.drawcoastlines()
	#m.fillcontinents(color='coral',lake_color='aqua')
	m.fillcontinents()
	# draw parallels and meridians.
	m.drawparallels(np.arange(-90.,120.,30.))
	m.drawmeridians(np.arange(0.,420.,60.))
	m.drawmapboundary()
	
	#plt.title("Mollweide Projection, Ray path");    # ipdb.set_trace()
	    # ipdb.set_trace()
		
	if Ser_name == '/IRIS/':
		plt.title("IRIS");
		lons_sta_float = []
		lats_sta_float = []
		for X in lons_sta:
			lons_sta_float.append(float(X))
		for X in lats_sta:
			lats_sta_float.append(float(X))
		x, y = m(lons_sta_float, lats_sta_float)
		color = 'blue'
		color1 = 'red'
	elif Ser_name == '/ARC/':
		plt.title("Arclink");
		x, y = m(lons_sta, lats_sta)
		color = 'blue'
		color1 = 'cyan'
	
	m.scatter(x, y, 20, color=color1, marker="v", edgecolor="k", zorder=10)

	for i in range(0, len(names_sta)):
		#plt.text(x[i], y[i], ' ' + names_sta[i], va="top", family="monospace", weight="bold")
		plt.text(x[i], y[i], ' ', va="top", size = 'x-small', family="monospace", weight="bold")
		
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 20, color="black", marker="o", edgecolor="k", zorder=3)
	
	# Return the great circles drawn from one event to all stations
	if Ser_name == '/IRIS/':
		for i in range(0, len(lats_sta)):
			m.drawgreatcircle(lon_event, lat_event, lons_sta_float[i], lats_sta_float[i], \
			color = color, zorder=2, linestyle='-')
		plt.text(x, y, ' ' + name_event, va="top", family="monospace", color = 'black', size = 'x-small', weight="bold")
		plt.savefig(Address + '/Data/' + Period + '/' + events[file_name]['event_id'] + '/IRIS/' + str(file_name) + '.pdf')
	
	elif Ser_name == '/ARC/':
		for i in range(0, len(lats_sta)):
			m.drawgreatcircle(lon_event, lat_event, lons_sta[i], lats_sta[i], \
			color = color, linestyle='-')
		plt.text(x, y, ' ' + name_event, va="top", size = 'x-small', family="monospace", weight="bold")
		plt.savefig(Address + '/Data/' + Period + '/' + events[file_name]['event_id'] + '/Arc_BH/' + str(file_name) + '.pdf')

	
'''
# ------------------------Trash-----------------------------
#poly = m.tissot(lon,lat,0.5,100, facecolor='green',zorder=10,alpha=0.5)
#poly = m.tissot(20,lat,0.5,200, facecolor='blue',zorder=10,alpha=0.5)
#poly = m.tissot(30,lat,0.5,1, facecolor='red',zorder=10,alpha=0.5)
	
	
	
"""
m1 = Basemap(projection='ortho', lat_0 = 50, lon_0 = 100, \
	resolution = 'l', area_thresh = 1000.)
m1.drawcoastlines()
m1.drawcountries()
#m.fillcontinents(color = 'coral')
m1.drawmapboundary()
m1.drawmeridians(np.arange(0, 360, 30))
m1.drawparallels(np.arange(-90, 90, 30))	

	

x, y = m1(lons_sta, lats_sta)
m1.plot(x,y,'bo')
	
for i in range(0, len(lats_sta)):
	m1.drawgreatcircle(lon_event, lat_event, lons_sta[i], lats_sta[i], \
	color = 'b', linestyle='-')

#plt.text(x, y, ' ' + name_event, va="top", family="monospace", weight="bold")
	
plt.savefig('/home/kasra/Desktop/fig3.pdf')
"""
"""
m2 = Basemap(projection='ortho', lat_0 = 50, lon_0 = 100, \
	resolution = 'l', area_thresh = 1000.)
m2.drawcoastlines()
m2.drawcountries()
#m.fillcontinents(color = 'coral')
m2.drawmapboundary()
m2.drawmeridians(np.arange(0, 360, 30))
m2.drawparallels(np.arange(-90, 90, 30))	

x, y = m2(lons_sta, lats_sta)
m2.plot(x,y,'bo')

plt.savefig('/home/kasra/Desktop/fig4.pdf')
"""

#ray_path()
#ray_path(lons_sta = [0, 10, 60, 120], lats_sta = [0, 40, -40, 30], names_sta = ['1', '2', '3', '4'])
'''
