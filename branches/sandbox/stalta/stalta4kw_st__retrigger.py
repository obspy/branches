#!/usr/bin/env python
"""
Recursive STA/LTA trigger for Unterhaching subnet.
"""
# 2009-07-23 Moritz; PYTHON2.5 REQUIRED
# 2009-11-25 Moritz
# 2010-09 Tobi
# 2011-01 Tobi

import matplotlib
matplotlib.use("AGG")

import os
import sys
import glob
from urllib2 import HTTPError
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from obspy.core import read, UTCDateTime, Stream, AttribDict
from obspy.signal import recStalta, triggerOnset, seisSim, cornFreq2Paz, bandpass
from obspy.seishub import Client
from matplotlib.mlab import detrend_linear as detrend


STATIONS = {'KW1': {'network': "BW", 'channel': "EHZ"},
            'KW2': {'network': "BW", 'channel': "EHZ"},
            'KW3': {'network': "BW", 'channel': "EHZ"}}
PAR = dict(LOW=10.0, # bandpass low corner
           HIGH=20.0, # bandpass high corner
           STA=0.5, # length of sta in seconds
           LTA=10, # length of lta in seconds
           ON=3.5, # trigger on threshold
           OFF=1, # trigger off threshold
           ALLOWANCE=1, # time in seconds to extend trigger-off time
           MAXLEN=10, # maximum trigger length in seconds
           MIN_STATIONS=3) # minimum of coinciding stations for alert
PAR = AttribDict(PAR)
SUMMARY = "/scratch/kw_trigger/kw_trigger.txt"
PLOTDIR = "/scratch/kw_trigger/"
MAILTO = ("megies",)


client = Client()

#for T1 in [UTCDateTime("2010-12-20T17:00:00"), UTCDateTime("2010-12-20T17:15:00"), UTCDateTime("2010-12-20T17:30:00"), UTCDateTime("2010-12-20T17:45:00")]:
    #T2 = T1 + (60 * 60 * 0.25) + 30
T1 = UTCDateTime("2011-09-19T08:00:00Z")
while T1 < UTCDateTime():
    T1 += (60 * 60 * 1)
    T2 = T1 + (60 * 60 * 1) + 30

    st = Stream()
    num_stations = 0
    exceptions = []
    for station, sta_info in STATIONS.iteritems():
        network = sta_info['network']
        channel = sta_info['channel']
        try:
            # we request 60s more at start and end and cut them off later to avoid
            # a false trigger due to the tapering during instrument correction
            tmp = client.waveform.getWaveform(network, station, "", channel,
                                              T1 - 60, T2 + 60, getPAZ=True,
                                              getCoordinates=True)
        # XXX adjust to currently randomly popping up HTTP 500 Error
        except HTTPError:
            ok = False
            for _i in xrange(20):
                try:
                    tmp = client.waveform.getWaveform(NET, station, "",
                            CHANNEL, T1 - 60, T2 + 60, getPAZ=True,
                            getCoordinates=True)
                    ok = True
                    exceptions.append("could fetch data after %s tries." % (_i + 2))
                    break
                except:
                    pass
            if not ok:
                exceptions.append("couldnt fetch data after 20 tries.")
                continue
        except Exception, e:
            exceptions.append("%s: %s" % (e.__class__.__name__, e.message))
            continue
        st.extend(tmp)
        num_stations += 1
    st.merge(-1)
    st.sort()

    summary = []
    summary.append("#" * 79)
    summary.append("######## %s  ---  %s ########" % (T1, T2))
    summary.append("#" * 79)
    summary.append(str(st))
    if exceptions:
        summary.append("#" * 33 + " Exceptions  " + "#" * 33)
        summary += exceptions
    summary.append("#" * 79)

    trigger_list = []
    if st:
        # preprocessing, backup original data for plotting at end
        st.merge(0)
        for tr in st:
            tr.data = detrend(tr.data)
        st.simulate(paz_remove="self", paz_simulate=cornFreq2Paz(1.0), remove_sensitivity=False)
        st.sort()
        st_trigger = st.copy()
        st_trigger.filter("bandpass", freqmin=PAR.LOW, freqmax=PAR.HIGH, corners=1, zerophase=True)
        st.trim(T1, T2)
        st_trigger.trim(T1, T2)
        st_trigger.trigger("recstalta", sta=PAR.STA, lta=PAR.LTA)

        # do the triggering
        for tr in st_trigger:
            tr.stats.channel = "recstalta"
            max_len = PAR.MAXLEN * tr.stats.sampling_rate
            trigger_sample_list = triggerOnset(tr.data, PAR.ON, PAR.OFF, max_len=max_len)
            for on, off in trigger_sample_list:
                 begin = tr.stats.starttime + float(on) / tr.stats.sampling_rate
                 end = tr.stats.starttime + float(off) / tr.stats.sampling_rate
                 trigger_list.append((begin.timestamp, end.timestamp, tr.stats.station))
        trigger_list.sort()

        # merge waveform and trigger stream for plotting
        # the normalizations are done because the triggers have a completely different
        # scale and would not be visible in the plot otherwise...
        st.filter("bandpass", freqmin=1.0, freqmax=20.0, corners=1, zerophase=True)
        st.normalize(global_max=False)
        st_trigger.normalize(global_max=True)
        st.extend(st_trigger)

        # coincidence part, work through sorted trigger list...
        mutt_base = ["mutt", "-s", "KW Alert  %s -- %s" % (T1, T2)]
        mutt = [] + mutt_base
        last_off_time = 0
        while len(trigger_list) > 1:
            on, off, sta = trigger_list[0]
            stations = []
            stations.append(sta)
            for i in xrange(1, len(trigger_list)):
                tmp_on, tmp_off, tmp_sta = trigger_list[i]
                # skip retriggering of already present station in current trigger
                if tmp_sta in stations:
                    continue
                if tmp_on < off + PAR.ALLOWANCE:
                    stations.append(tmp_sta)
                    # allow sets of triggers that overlap only on subsets of all
                    # stations (e.g. A overlaps with B and B overlaps with C => ABC)
                    off = max(off, tmp_off)
                else:
                    break
            # process event if enough stations reported it
            if len(set(stations)) >= PAR.MIN_STATIONS:
                if off != last_off_time:
                    event = (UTCDateTime(on), off - on, stations)
                    summary.append("%s %04.1f %s" % event)
                    #tmp = st.slice(UTCDateTime(on), UTCDateTime(off))
                    tmp = st.slice(UTCDateTime(on) - 1, UTCDateTime(off))
                    outfilename = "%s/%s_%.1f_%s-%s_%s.png" % (PLOTDIR, UTCDateTime(on), off - on, len(stations), num_stations, "-".join(stations))
                    tmp.plot(outfile=outfilename)
                    mutt += ("-a", outfilename)
                    last_off_time = off
            # just move a single line ahead, do not skip more than one line.
            # this could miss an event.
            # this is of course a bit slower but its also safer.
            trigger_list = trigger_list[1:]

    summary = "\n".join(summary)
    summary += "\n" + "\n".join(("%s=%s" % (k, v) for k, v in PAR.items()))
    #print summary
    open(SUMMARY, "at").write(summary + "\n")
    # send emails
    if MAILTO:
        mutt += MAILTO
        sub = subprocess.Popen(mutt, stdin=subprocess.PIPE)
        sub.communicate(summary)
        # send again without attachments if mutt had a problem (too many images)
        if sub.returncode != 0:
            mutt = mutt_base + MAILTO
            sub = subprocess.Popen(mutt, stdin=subprocess.PIPE)
            sub.communicate(summary)

    plt.close('all')
    del st
    del tmp
    del st_trigger
    del summary
    del tr
    del trigger_list
    del trigger_sample_list
    del mutt
