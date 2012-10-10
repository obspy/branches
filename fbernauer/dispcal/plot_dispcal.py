#! /usr/bin/env python

################################################
# Skript zum Plotten der dispcal Ausgabe Files #
################################################

"""
USAGE: ./plot_tiltcal.py <dispcal_???.txt> 
"""

import sys, math
import matplotlib.pyplot as plt
import numpy as np
from obspy.core import *

if len(sys.argv) < 2:
   print __doc__
   sys.exit(1)



data_array1 = np.loadtxt(sys.argv[1])


fig = plt.figure()
ax1 = plt.subplot(111)
ax1.plot(data_array1, color='r', label=sys.argv[1])
ax1.legend()

plt.show()
