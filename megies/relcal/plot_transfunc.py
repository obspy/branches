#! /usr/bin/env python

# Tool for plotting the transferfunction calculated with relcaltack

"""
USAGE: %s input file
"""

USAGE = '%s input file'

import sys
import numpy as np
import matplotlib.pyplot as plt

# read input file
try:
    file = sys.argv[1]
except:
    raise USAGE

data = np.loadtxt(file)
# create array with data from file
fr = data[:,0]
amp = data[:,1]
phase = data[:,2]

# plot
fig = plt.figure()
# make a little extra space between the subplots
plt.subplots_adjust(hspace=0.5)
ax1 = plt.subplot(211)
ax1.loglog(fr, amp)
ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Amplitude')
ax1.set_title('unknown transfer function')
ax2 = plt.subplot(212)
ax2.semilogx(fr, phase)
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Phase [rad]')

plt.show()

