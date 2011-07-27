"""
Plot a map that shows all requested events...
ATTENTION: llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat --> have been imported for local plotting
"""

import pickle
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

def plot_all_events(input, Address_events, events, lon_event, lat_event, name_event, len_events):
	
	plt.clf()
	
	# lon_0 is central longitude of projection.
	# resolution = 'c' means use crude resolution coastlines.
	
	# lat_0=lat_event[0], determines that center of the map has been aligend to the first event
	
	m = Basemap(projection='moll', lon_0=lon_event[0], lat_0=lat_event[0], resolution='c')
	#m = Basemap(projection='moll', lon_0=180, lat_0=0, resolution='c')
	
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
	
	#plt.title("Mollweide Projection, Events");
	plt.title("Events");
	
	x, y = m(lon_event, lat_event)
	m.scatter(x, y, 40, color="red", marker="o", edgecolor="k", zorder=3)
	
	for i in range(0, len_events):
		plt.text(x[i], y[i], ' ' + name_event[i], va="top", family="monospace", \
		color = 'black', size = 'x-small', weight="bold")
	
	plt.savefig(Address_events + '/Plot_events' + '.pdf')
