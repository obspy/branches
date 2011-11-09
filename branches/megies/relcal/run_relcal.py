#! /usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')
import os
from obspy.core import read
from obspy.signal.calibration import relcalstack
import matplotlib.pyplot as plt

cwd = os.getcwd()

st1 = read('%s/CA.STS2..EHZ.D.2011.046.2h'%(cwd))
st2 = read('%s/CA.0438..EHZ.D.2011.046.2h'%(cwd))
#st1 = read('%s/mb_new'%(cwd))
#st2 = read('%s/w_new'%(cwd))

#calfile = "%s/MB2005_simp.cal"%(cwd)
calfile = "%s/STS2_simp.cal"%(cwd)


freq, amp, phase = relcalstack(st1, st2, calfile, 600, smooth=0)

 # plot
fig = plt.figure()
 # make a little extra space between the subplots
plt.subplots_adjust(hspace=0.5)
ax1 = plt.subplot(211)
ax1.loglog(freq, amp)
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Amplitude')
ax1.set_title('unknown transfer function')
ax2 = plt.subplot(212)
ax2.semilogx(freq, phase)
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Phase [rad]')
 
plt.show()
