#!/usr/bin/env python
#-------------------------------------------------------------------
# Filename: relcalstack.py
#  Purpose: Functions for relative calibration (e.g. Huddle test calibration)
#   Author: Felix Bernauer, Simon Kremers
#    Email: bernauer@geophysik.uni-muenchen.de
#
# Copyright (C) 2011 Felix Bernauer, Simon Kremers
#---------------------------------------------------------------------
"""
Functions for relative calibration

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

import math
import sys
import warnings
import numpy as np
from obspy.signal.util import nextpow2
from obspy.core import Stream
from konno_ohmachi_smoothing import smooth_spectra
from calcresp import calcresp
from matplotlib.mlab import _spectral_helper as spectral_helper

def relcalstack(st1, st2, calib_file, window_len, OverlapFrac=0.5, smooth=0):
    """
    Method for relative calibration of sensors using a sensor with known transfer function

    :param st1/st2: Stream object, (known/unknown) the trace.stats dict like class must contain \
                    the parameters "sampling_rate", "npts" and "station"
    :type calib_file: String
    :param calib_file: name of calib file containing the known PAZ of known instrument in GSE2 standard.
    :type window_len: Float
    :param window_len: length of sliding window in seconds
    :type OverlapFrac: float
    :param OverlapFrac: fraction of overlap, defaults to fifty percent (0.5)
    :type smooth: Float
    :param smooth: variable that defines if the Konno-Ohmachi taper is used or not. default = 0 -> no taper \
                    generally used in geopsy: smooth = 40
    """
    # check Konno-Ohmachi
    if smooth < 0:
        smooth = 0
                                                                   
    # check if sampling rate and trace length is the same
    if st1[0].stats.npts != st2[0].stats.npts:
        msg = 'Traces dont have the same length!'
        raise ValueError(msg)
    elif st1[0].stats.sampling_rate != st2[0].stats.sampling_rate:
        msg = 'Traces dont have the same sampling rate!'
        raise ValueError(msg)
    else:
        ndat1 = st1[0].stats.npts
        ndat2 = st2[0].stats.npts
        sampfreq = st1[0].stats.sampling_rate

    # read waveforms
    tr1 = st1[0].data.astype(np.float64)
    tr2 = st2[0].data.astype(np.float64)
                                                 
    # get window length, nfft and frequency step
    ndat = int(window_len*sampfreq)
    nfft = nextpow2(ndat)
    df = sampfreq / nfft

    # initialize array for response function
    res = np.zeros(nfft/2+1, dtype='complex128')

    # read calib file and calculate response function
    gg, freq = calcresp(calib_file, nfft, sampfreq)

    # calculate number of windows and overlap
    nwin = int(np.floor((ndat1 - nfft)/(nfft/2)) + 1)
    noverlap = nfft * OverlapFrac

    auto, freq, t = spectral_helper(tr1, tr1, NFFT=nfft, Fs=sampfreq, noverlap = noverlap)
    cross, freq, t = spectral_helper(tr1, tr2, NFFT=nfft, Fs=sampfreq, noverlap = noverlap)
    
    # 180 Grad Phasenverschiebung
    cross.imag = -cross.imag

    for i in range(nwin): 
        res += (cross[:,i] / auto[:,i]) * gg
    
    # apply Konno-Ohmachi smoothing taper if choosen
    if smooth > 0:
        res /= nwin                             

        res.real = smooth_spectra(res.real, freq, smooth, count=1, max_memory_in_mb=1024)
        res.imag = smooth_spectra(res.imag, freq, smooth, count=1, max_memory_in_mb=1024) 

    else:
        res /= nwin

    #print 'Writing output....'
                                                                                  
    f = open(st2[0].stats.station+"."+str(window_len)+".resp", "w")
    g = open(st1[0].stats.station+".refResp", "w")

    amp = []
    phase = []

    for i in range(nfft/2+1):

        a = np.sqrt(res.real[i]*res.real[i]+res.imag[i]*res.imag[i]) 
        pha = np.arctan2(res.imag[i],res.real[i])
        ra = np.sqrt(gg.real[i]*gg.real[i]+gg.imag[i]*gg.imag[i])
        rpha = np.arctan2(gg.imag[i],gg.real[i])
        amp.append(a)
        phase.append(pha)
        f.write("%f %f %f\n" %(freq[i], a, pha))
        g.write("%f %f %f\n" %(freq[i], ra, rpha))

    f.close()
    g.close()

    return freq, amp, phase


