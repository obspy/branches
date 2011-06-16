"""
Return the locations of all requested events...
"""

import pickle
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

def plot_all_events(Address_events, events, lon_event, lat_event, name_event, Num_Event):
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	m = Basemap(projection='moll', lon_0=lon_event[0], lat_0=lat_event[0], resolution='c')
	
	# Different Options for drawing the Earth:
	#m = Basemap(projection='lcc',lon_0=0,resolution='c')
	#m.bluemarble()
	#m.drawcountries(linewidth=2)
	
	m.drawcoastlines()
	m.fillcontinents(color='coral',lake_color='aqua')

	# draw parallels and meridians.
	m.drawparallels(np.arange(-90.,120.,30.))
	m.drawmeridians(np.arange(0.,420.,60.))
	m.drawmapboundary(fill_color='aqua') 
	
	plt.title("Mollweide Projection, Events");
	#plt.title("Events, 02.01.2008-01.05.2011");
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 20, color="b", marker="o", edgecolor="k", zorder=3)
	'''
	for i in range(0, Num_Event):
		plt.text(x[i], y[i], ' ' + name_event[i], va="top", family="monospace", weight="bold")
	'''
	plt.savefig(Address_events + '/All_events' + '.pdf')	
