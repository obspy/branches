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
    stream = sys.argv[1]
    utctime = sys.argv[2]
    duration = float(sys.argv[3])
    mother = sys.argv[4]
    bb = int(sys.argv[5])
    what = sys.argv[6]
except:
    usage = 'Usage: %s Net.Stat.loc.channel %s UTCtime %f duration %s wavelet %d bb %s Amp/Phase <outfile>'
    print usage; sys.exit(1)

try: 
    outfile = sys.argv[7]
    format = 'png'
    outfile = string.join((outfile,format),'.')
except:
    usage = 'Usage: %s Net.Stat.loc.channel %s UTCtime %f duration %s wavelet %d bb %s Amp/Phase <outfile>'
    print usage; 


t = UTCDateTime(utctime)
net,stat,loc,chan = stream.split(".")
pz = client.station.getPAZ(net, stat,t,'', chan)
sz = client.waveform.getWaveform(net,stat,loc, chan, t, t+duration)

df = sz[0].stats.sampling_rate
npts = sz[0].stats.npts
data = (sz[0].data - sz[0].data.mean()) /pz['sensitivity']


def scaleogram(data, samp_rate = 100.0,wavelet = 'morlet' ,bb=6,what = 'Amp',axis = None):
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


    dscale = 0.1
    dtime = 1./samp_rate
    npts = data.shape[0]
    tt = np.arange(0,npts/samp_rate,1/samp_rate)
    xx = ml.autoscales(N=data.shape[0], dt=dtime, dj=dscale, wf=wavelet, p=bb)
    X = ml.cwt(x=data, dt=dtime, scales=xx, wf=wavelet, p=bb)
    freq = ml.fourier_from_scales(xx, wavelet, bb)
    freq = 1./freq

#    amp = X
    amp = np.abs(X)
    phase = np.angle(X)

    if not axis:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    else:
        ax = axis

    ax.set_yscale('log')
    if what == 'Amp':
        im=ax.pcolormesh(tt,freq,amp)
    else:
        im=ax.pcolormesh(tt,freq,phase)

    # set correct way of axis, whitespace before and after with window
    # length

    ax.axis('tight')
    # ax.set_xlim(0, end)
    ax.grid(False)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Frequency [Hz]')

    if axis:
        return ax, im


T = np.arange(0,npts/df,1/df)
fig = plt.figure()
ax1 = fig.add_axes([0.1, 0.75, 0.7, 0.2])
#data = data/pz["sensitivity"]
ax1.plot(T,data,'k')
ax1.set_title("%s Station %s" % (t,sz[0].stats.station))
ax1.set_ylabel('velocity [m/s]')
ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60])
ax3 = fig.add_axes([0.83,0.1,0.03,0.6])
ax, spec = scaleogram(data, samp_rate=df, wavelet=mother,bb=bb,what=what,axis=ax2)
ax1.set_xlim(T[0], T[-1])
ax2.set_xlim(T[0], T[-1])
fig.colorbar(spec, cax=ax3)
if outfile:
    plt.savefig(outfile,format=format)
else:
    plt.show()

