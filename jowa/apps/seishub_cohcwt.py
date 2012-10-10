#!/usr/bin/env python
import numpy as np
import scipy as sp
from obspy.core import UTCDateTime, read, Trace
from obspy.seishub import Client
import sys, string
from matplotlib import mlab
import matplotlib.pyplot as plt
import obspy.signal
import mlpy.wavelet as ml

client = Client(base_url='http://10.153.82.3:9080', user='admin',password='admin', timeout=10)

try:
    stream1 = sys.argv[1]
    stream2 = sys.argv[2]
    utctime = sys.argv[3]
    duration = float(sys.argv[4])
    mother = sys.argv[5]
    bb = int(sys.argv[6])
    what = sys.argv[7]
except:
    usage = 'Usage: %s Net.Stat.Loc.Chan %s Net.Stat.Loc.Chan %s UTCtime %f duration %s wavelet %d bb %s Amp/Phase <outfile>'
    print usage; sys.exit(1)

try: 
    outfile = sys.argv[8]
    format = 'png'
    outfile = string.join((outfile,format),'.')
except:
    usage = 'Usage: %s Net.Stat.Loc.Chan %s Net.Stat.Loc.Chan %s UTCtime %f duration %s wavelet %d bb %s Amp/Phase <outfile>'
    print usage; 


t = UTCDateTime(utctime)
net1,stat1,loc1,chan1 = stream1.split(".")
pz1 = client.station.getPAZ(net1, stat1,t,'', chan1)
sz1 = client.waveform.getWaveform(net1,stat1,loc1, chan1, t, t+duration)
sz1.merge()
print sz1

df1 = sz1[0].stats.sampling_rate
npts1 = sz1[0].stats.npts
data1 = (sz1[0].data - sz1[0].data.mean()) /pz1['sensitivity']

net2,stat2,loc2,chan2 = stream2.split(".")
pz2 = client.station.getPAZ(net2, stat2,t,'', chan2)
sz2 = client.waveform.getWaveform(net2,stat2,loc2, chan2, t, t+duration)
sz2.merge()
print sz2

df2 = sz2[0].stats.sampling_rate
npts2 = sz2[0].stats.npts
data2 = (sz2[0].data - sz2[0].data.mean()) /pz2['sensitivity']

if df1 != df2:
    print "Sampling rates not the same, exit!!"; sys.exit(1)

if npts1 != npts2:
    print "Number of data points not the same, exit!!"; sys.exit(1)

def ratio_scaleogram(data1,data2, samp_rate = 100.0,wavelet = 'morlet' ,bb=6,what = 'Amp',axis = None):
    """
    Computes and plots logarithmic spectrogram of the input trace.

    :param data: Input data
    :param sample_rate: Samplerate in Hz
    :param log: True logarithmic frequency axis, False linear frequency axis
    :param per_lap: Percent of overlap
    :param nwin: Approximate number of windows.
    :param outfile: String for the filename of output file, if None
        interactive plotting is activated.
    :param format: Format of image to save
    :param axis: Plot into given axis, this deactivates the format and
        outfile option
    """
    # enforce float for samp_rate
    samp_rate = float(samp_rate)

    # nfft needs to be an integer, otherwise a deprecation will be raised


    dscale = 0.05
    dtime = 1./samp_rate
    npts = data1.shape[0]
    tt = np.arange(0,npts/samp_rate,1/samp_rate)
    xx = ml.autoscales(N=data1.shape[0], dt=dtime, dj=dscale, wf=wavelet, p=bb)
    X = ml.cwt(x=data1, dt=dtime, scales=xx, wf=wavelet, p=bb)
    Y = ml.cwt(x=data2, dt=dtime, scales=xx, wf=wavelet, p=bb)
    freq = ml.fourier_from_scales(xx, wavelet, bb)
    freq = 1./freq

    XY = np.abs(X*Y.conjugate())
    YY = np.abs(Y*Y.conjugate())
    XX = np.abs(X*X.conjugate())
    ss,st = XY.shape

    s = np.arange(dscale,0.6,dscale)

    i= 0
    Tl = bb
    while i < ss:
        bt = np.kaiser(Tl*(i+1),0)
        XY[i,:] = np.convolve(XY[i,:],bt,'same')
        XX[i,:] = np.convolve(XX[i,:],bt,'same')
        YY[i,:] = np.convolve(YY[i,:],bt,'same')
        i += 1

    Tf = bb
    i = 0
    while i < st:
        s = np.kaiser(Tf,0)
        XY[:,i] = np.convolve(XY[:,i],s,'same')
        XX[:,i] = np.convolve(XX[:,i],s,'same')
        YY[:,i] = np.convolve(YY[:,i],s,'same')
        i += 1

    Coh = (np.abs(XY)**2)/(np.abs(XX) * np.abs(YY))


    if not axis:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    else:
        ax = axis

    ax.set_yscale('log')
    im=ax.pcolormesh(tt,freq,Coh)

    # set correct way of axis, whitespace before and after with window
    # length

    ax.axis('tight')
    # ax.set_xlim(0, end)
    ax.grid(False)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Frequency [Hz]')

    if axis:
        return ax, im

T = np.arange(0,npts1/df1,1/df1)
fig = plt.figure()
ax1 = fig.add_axes([0.1, 0.85, 0.7, 0.09])
ax1.plot(T,data1,'k')
ax4 = fig.add_axes([0.1, 0.75, 0.7, 0.09])
ax4.plot(T,data2,'k')
ax1.set_title("%s  %s vs. %s" % (t,sz1[0].stats.station,sz2[0].stats.station))
ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60])
ax3 = fig.add_axes([0.83,0.1,0.03,0.6])
ax, spec = ratio_scaleogram(data1,data2, samp_rate=df1, wavelet=mother,bb=bb,what=what,axis=ax2)
ax1.set_xlim(T[0], T[-1])
ax4.set_xlim(T[0], T[-1])
ax2.set_xlim(T[0], T[-1])
fig.colorbar(spec, cax=ax3)
if outfile:
    plt.savefig(outfile,format=format)
else:
    plt.show()


