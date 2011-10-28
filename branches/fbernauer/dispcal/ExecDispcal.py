#! /usr/bin/env python

import optparse
import matplotlib.pyplot as plt
import numpy as np
from dispcal import dispcal
from obspy.core import *

usage = '...'
parser = optparse.OptionParser(usage)

parser.add_option('-f', '--filename', type=str, dest='filename',
                    default='',
                    help='name of file containing data')
parser.add_option('--corn_freq', type=float, dest='corn_freq',
                    default=0.98,
                    help='corner frequency of seismometer')
parser.add_option('--damping', type=float, dest='damping',
                    default=0.6,
                    help='damping coefiient of seismometer')
parser.add_option('--bit_weight', type=float, dest='bit_weight',
                    default=1.589e-6,
                    help='digitizer bit weight in microvolts / count')
parser.add_option('--disp', type=float, dest='displ',
                    default=1.003,
                    help='absolute displacement in mm')
parser.add_option('--gap', type=float, dest='gap',
                    default=0.0,
                    help='safety distance from pulse flanks in seconds (has to be specified in this version)')
parser.add_option('--bfc', type=float, dest='bfc',
                    default=0.0,
                    help='corner freq of butterworth filter')
parser.add_option('--bm', type=int, dest='bm',
                    default=0,
                    help='order of butterworth filter')
#parser.add_option('--int', type=bol, dest='int',
#                    default=False,
#                    help='set True if integration is required')

(options, args) = parser.parse_args()

file_name = options.filename
st = read(file_name)
data = st[0].data
samprate = st[0].stats.sampling_rate

bfc = options.bfc
bm = options.bm
fcs = options.corn_freq
hs = options.damping
gap = options.gap
dgain = options.bit_weight
step = options.displ

inst_name = st[0].stats.station

print ''
print 'Absolute calibration of instrument: ' + inst_name + '.'
print 'Transfer function:'
print '    corner frequency: ' + str(fcs)
print '             damping: ' + str(hs)
print '-----------------------------------------------------------------'
print ''




raw, deconv, displ, marks = dispcal(data, samprate, fcs, hs, gap, dgain, step, bfc=0.0, bm=0)

lo = np.empty(len(marks))
hi = np.empty(len(marks))
for i in range(len(marks)):
    lo[i] = marks[i][0] 
    hi[i] = marks[i][1] 
# PLOT
fig = plt.figure()
ax1 = plt.subplot(311)
ax1.plot(raw, label='(filtered) raw data')
plt.legend()

ax2 = plt.subplot(312)
ax2.plot(deconv, label='real ground movement')
for i in range(len(marks)):
    ax2.axvline(lo[i], color='g')
    ax2.axvline(hi[i], color='r')
plt.legend()

ax3 = plt.subplot(313)
ax3.plot(displ, label='real displacement')
for i in range(len(marks)):
    ax3.axvline(lo[i], color='g')
    ax3.axvline(hi[i], color='r')
plt.legend()

plt.show()
