#! /usr/bin/env python

import sys
import matplotlib
matplotlib.use('TkAgg')
import os
from obspy.core import read,UTCDateTime
from obspy.signal import calibration
import matplotlib.pyplot as plt

usage = 'Usage: %s file_known %s file_unknown %s calibration %f window [s] %d smoothing (points) %s start_time %s end_time'

cwd = os.getcwd()

try:
     known  = sys.argv[1]
     unknown  = sys.argv[2]
     calfile  = sys.argv[3]
     window  = float(sys.argv[4])
     sxm  = int(sys.argv[5])
     start = sys.argv[6]
     end = sys.argv[7]
except:
     print usage; sys.exit(1)


st1 = read('%s/%s'%(cwd,known))
st1.merge()
st2 = read('%s/%s'%(cwd,unknown))
st2.merge()
st = UTCDateTime(start)
ed = UTCDateTime(end)
st1.trim(st,ed)
st2.trim(st,ed)
print st1
print st2
calfile = "%s/%s"%(cwd,calfile)


freq, amp, phase = calibration.relcalstack(st1, st2, calfile, window, overlap_frac=0.5,smooth=sxm)

 # plot
fig = plt.figure()
 # make a little extra space between the subplots
plt.subplots_adjust(hspace=0.5)
ax1 = plt.subplot(211)
ax1.loglog(freq, amp)
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Amplitude')
ax1.set_xlim(1,100)
ax1.set_title('unknown transfer function')
ax2 = plt.subplot(212)
ax2.semilogx(freq, phase)
ax2.set_xlim(1,100)
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Phase [rad]')
 
plt.show()
