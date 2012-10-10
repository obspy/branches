#! /usr/bin/env python

##############################################
# Skript zum Plotten der calex Ausgabe Files #
##############################################

"""
USAGE: ./plot_calex_out.py <calex5a file> <calex.py file> 
"""

import sys, math
import matplotlib.pyplot as plt
import numpy as np
from obspy.core import *

if len(sys.argv) < 2:
   print __doc__
   sys.exit(1)

infilename = sys.argv[1]
ifile = open(infilename,'r')

data = []
for line in ifile:
    l = line.split()
    for i in np.arange(0,len(l),1):
        data.append(l[i])


data_array1 = np.asarray(data[8:],dtype='float64')
data_array2 = np.loadtxt(sys.argv[2])
np.savetxt(sys.argv[1]+'.a', data_array1)

#st_einf = read(sys.argv[2])
#st_ausf = read(sys.argv[3])
#st_simulate = read(sys.argv[2]) 

fig = plt.figure()
ax1 = plt.subplot(111)
ax1.plot(data_array1, color='b', label='dispcal5.f')
ax1.plot(data_array2, color='r', label='dispcal.py')
#ax1.plot(st_einf[0].data, color='g',label='calex.py')
#ax1.plot(st_ausf[0].data, color='r',label='eing')
#ax1.plot(st_simulate[0].data, color='r',label='simulate')
ax1.legend()

plt.show()
