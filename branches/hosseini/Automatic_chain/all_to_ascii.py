"""
Generate the ASCII file from ALL available waveforms (streams)
"""

from obspy.core import read

# Selecting target seismograms based on desired parameters, such as GCARC, is the goal of this code.
# There are two different methods...the second one is highly recommended.
# 1. A directory will be copied to the local directory. tar and ... files should be deleted (user should check whether there is any or not). Finally, search for the required stations...
# 2. Working on the directory available in the server without copying, deleting or...Since we have omitted both previous steps and any user intervention, this method is significantly faster than previous one...and highly recommended!

# Contents:
# (OLD VERSION) a directory as an input, remove the tar files and determine the requied Stations (based on GCARC)--------------------
# (NEW VERSION) Modified version for selecting the target stations...
# Trash...


from obspy.core import read
from obspy.core import path
import numpy as np
import matplotlib.pyplot as plt
import os
from shutil import copytree
from shutil import rmtree
import glob

def all_to_ascii(Period, event, Address = '/media/6F8274DF3246729C/ARCLINK TEST'):
	# NEW VERSION
	# Modified version for selecting the target stations...
	# In this part, the code will not copy the directory or... . It uses the directory available in the server to select the required stations
	
	#import ipdb; ipdb.set_trace()
	
	List_Stations_BHE = glob.glob(Address + '/Data/' + Period + '/' + event['event_id'] + '/Arc_BH/*-BHE')
	List_Stations_BHN = glob.glob(Address + '/Data/' + Period + '/' + event['event_id'] + '/Arc_BH/*-BHN')
	List_Stations_BHZ = glob.glob(Address + '/Data/' + Period + '/' + event['event_id'] + '/Arc_BH/*-BHZ')

	Len_List_Stations_BHE = len(List_Stations_BHE)
	Len_List_Stations_BHN = len(List_Stations_BHN)
	Len_List_Stations_BHZ = len(List_Stations_BHZ)

#-------------BHE
	print "---------------BHE------------------"
	print Len_List_Stations_BHE

	for i in range(0, Len_List_Stations_BHE): 
		import ipdb; ipdb.set_trace()   
		st_station = read(List_Stations_BHE[i])
		for j in range(0, st_station[0].stats.npts):
			st_file = open(List_Stations_BHE[i], 'wr')
			#Address + '/Data/' + Period + '/' + \
			#event['event_id'] + '/Arc_BH/' + 
			st_file.writelines((1.0/st_station[0].stats.sampling_rate)*j + \
			'   ' + str(st_station[0].data[j]) + '\n') 
		st_file.close()
        
        
"""
	for i in range(0, len(b1)):
        print List_event_BHE[b1[i]]


	#-------------BHN

	print "---------------BHN------------------"
	print Len_List_event_BHN

	for i in range(1, Len_List_event_BHN+1):
        st_station = read(List_event_BHN[i-1])
        GCARC_Station = st_station[0].stats.sac.gcarc
        if GCARC_Station <= 30:
                #print "YES =" + str(GCARC_Station)
                #print List_event[i-1]
                #print i-1
                Target_Stations_BHN[i]=i

	a2 = np.nonzero(Target_Stations_BHN)
	b2 = a2[0]-1
	print "BHN components:"
	print ""
	print b2
	print ""
	print "Number of components in the range:"
	print len(b2)


	for i in range(0, len(b2)):
        print List_event_BHN[b2[i]]


	#-------------BHZ

	print "---------------BHZ------------------"
	print Len_List_event_BHZ

	for i in range(1, Len_List_event_BHZ+1):
        st_station = read(List_event_BHZ[i-1])
        GCARC_Station = st_station[0].stats.sac.gcarc
        if GCARC_Station <= 30:
                #print "YES =" + str(GCARC_Station)
                #print List_event[i-1]
                #print i-1
                Target_Stations_BHZ[i]=i

	a3 = np.nonzero(Target_Stations_BHZ)
	b3 = a3[0]-1
	print ""
	print "BHZ components:"
	print b3
	print ""
	print "Number of components in the range:"
	print len(b3)


	for i in range(0, len(b3)):
        print List_event_BHZ[b3[i]]
 """

