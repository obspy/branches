#!/usr/bin/env python

"""
USAGE: plotRelCalTime(on/off, scale, st_ein, st_aus, st_fin, st_diff)

switch: can be 0 or 1
     0: all the data is plotted on one axis
     1: data of each file is plotted on a seperated axis
scale : amplitude scale factor
"""

import sys, math
import numpy as np
from obspy.core import read
import matplotlib.pyplot as plt

#if len(sys.argv) < 4:
#    print __doc__
#    sys.exit(1)

def plotRelCalTime(switch, scale, amp, st_ein, st_aus, st_fin, st_diff):


    if switch == 1:
        fig = plt.figure()
        ax1 = plt.subplot(411)
        ax1.plot(st_ein[0].data * scale * amp)
        ax1.set_xlabel('Sample')
        ax1.set_ylabel('Amplitude \n '+'Generator')
        ax2 = plt.subplot(412)
        ax2.plot(st_aus[0].data * scale)
        ax2.set_xlabel('Sample')
        ax2.set_ylabel('Amplitude \n '+'real signal')
        ax3 = plt.subplot(413)
        ax3.plot(st_fin[0].data * scale)
        ax3.set_xlabel('Sample')
        ax3.set_ylabel('Amplitude \n '+'final simulated signal')
        ax4 = plt.subplot(414)
        ax4.plot(st_diff[0].data * scale)
        ax4.set_xlabel('Sample')
        ax4.set_ylabel('difference between \n real and simulated')
        plt.show()
    
    if switch == 0:
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(st_ein[0].data * scale * amp, label='Generator')
        ax.plot(st_aus[0].data * scale, label='real signal')
        ax.plot(st_fin[0].data * scale, label='final simulated signal')
        ax.plot(st_diff[0].data * scale, label='difference between real and simulated')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Amplitude')
        ax.legend()
        plt.show()
    
