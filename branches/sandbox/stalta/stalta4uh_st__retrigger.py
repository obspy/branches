#!/usr/bin/env python
"""
Recursive STA/LTA trigger for Unterhaching subnet.
"""
# 2009-07-23 Moritz; PYTHON2.5 REQUIRED
# 2009-11-25 Moritz
# 2010-09 Tobi

import matplotlib
matplotlib.use("AGG")

from urllib2 import HTTPError
import subprocess
import matplotlib.pyplot as plt
from obspy.core import UTCDateTime, Stream, AttribDict
from obspy.signal import coincidenceTrigger, cosTaper
from obspy.seishub import Client


NET = "BW"
STATIONS = ("DHFO", "UH1", "UH2", "UH3", "UH4")
CHANNEL = "EHZ"
PAR = dict(LOW=10.0, # bandpass low corner
           HIGH=20.0, # bandpass high corner
           STA=0.5, # length of sta in seconds
           LTA=10, # length of lta in seconds
           ON=3.5, # trigger on threshold
           OFF=1, # trigger off threshold
           ALLOWANCE=1.2, # time in seconds to extend trigger-off time
           MAXLEN=10, # maximum trigger length in seconds
           MIN_STATIONS=3) # minimum of coinciding stations for alert
PAR = AttribDict(PAR)
SUMMARY = "/scratch/uh_trigger/uh_trigger.txt"
PLOTDIR = "/scratch/uh_trigger/"
MAILTO = ["megies"]

client = Client("http://10.153.82.3:8080", timeout=60)

#for T1 in [UTCDateTime("2010-12-20T17:00:00"), UTCDateTime("2010-12-20T17:15:00"), UTCDateTime("2010-12-20T17:30:00"), UTCDateTime("2010-12-20T17:45:00")]:
    #T2 = T1 + (60 * 60 * 0.25) + 30
#T1 = UTCDateTime("2010-05-27T15:00:00Z")
#while T1 < UTCDateTime("2010-05-27T16:00:00Z"):
T1 = UTCDateTime("2012-07-19T05:00:00Z")
while T1 < UTCDateTime("2012-07-19T08:00:00Z"):
    T1 += (60 * 60 * 1)
    T2 = T1 + (60 * 60 * 1) + 30

    st = Stream()
    num_stations = 0
    exceptions = []
    for station in STATIONS:
        try:
            # we request 60s more at start and end and cut them off later to avoid
            # a false trigger due to the tapering during instrument correction
            tmp = client.waveform.getWaveform(NET, station, "", CHANNEL, T1 - 180,
                                              T2 + 180, getPAZ=True,
                                              getCoordinates=True)
        # XXX adjust to currently randomly popping up HTTP 500 Error
        except HTTPError:
            ok = False
            for _i in xrange(20):
                try:
                    tmp = client.waveform.getWaveform(NET, station, "",
                            CHANNEL, T1 - 180, T2 + 180, getPAZ=True,
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
            exceptions.append("%s: %s" % (e.__class__.__name__, e))
            continue
        st.extend(tmp)
        num_stations += 1
    st.merge(-1)
    st.sort()

    summary = []
    summary.append("#" * 79)
    summary.append("######## %s  ---  %s ########" % (T1, T2))
    summary.append("#" * 79)
    summary.append(st.__str__(extended=True))
    if exceptions:
        summary.append("#" * 33 + " Exceptions  " + "#" * 33)
        summary += exceptions
    summary.append("#" * 79)

    trig = []
    mutt = []
    if st:
        # preprocessing, backup original data for plotting at end
        st.merge(0)
        st.detrend("linear")
        for tr in st:
            tr.data = tr.data * cosTaper(len(tr), 0.01)
        #st.simulate(paz_remove="self", paz_simulate=cornFreq2Paz(1.0), remove_sensitivity=False)
        st.sort()
        st.filter("bandpass", freqmin=PAR.LOW, freqmax=PAR.HIGH, corners=1, zerophase=True)
        st.trim(T1, T2)
        st_trigger = st.copy()
        st.normalize(global_max=False)
        # do the triggering
        trig = coincidenceTrigger("recstalta", PAR.ON, PAR.OFF, st_trigger,
                thr_coincidence_sum=PAR.MIN_STATIONS,
                max_trigger_length=PAR.MAXLEN, trigger_off_extension=PAR.ALLOWANCE,
                details=True, sta=PAR.STA, lta=PAR.LTA)

        for t in trig:
            info = "%s %ss %s %s" % (t['time'].strftime("%Y-%m-%dT%H:%M:%S"), ("%.1f" % t['duration']).rjust(4), ("%i" % t['cft_peak_wmean']).rjust(3), "-".join(t['stations']))
            summary.append(info)
            tmp = st.slice(t['time'] - 1, t['time'] + t['duration'])
            outfilename = "%s/%s_%.1f_%i_%s-%s_%s.png" % (PLOTDIR, t['time'].strftime("%Y-%m-%dT%H:%M:%S"), t['duration'], t['cft_peak_wmean'], len(t['stations']), num_stations, "-".join(t['stations']))
            tmp.plot(outfile=outfilename)
            mutt += ("-a", outfilename)
        del tmp
        del st_trigger
        del tr
    del st

    summary.append("#" * 79)
    summary = "\n".join(summary)
    summary += "\n" + "\n".join(("%s=%s" % (k, v) for k, v in PAR.items()))
    #print summary
    open(SUMMARY, "at").write(summary + "\n")
    # send emails
    if MAILTO:
        alert_lvl = 0
        if len(trig) > 0:
            alert_lvl = 1
        for t in trig:
            if t['cft_peak_wmean'] > 7:
                alert_lvl = max(alert_lvl, 2)
            elif t['cft_peak_wmean'] > 10:
                alert_lvl = 3

        mutt_base = ["mutt", "-s", "UH Alert %d  %s - %s" % (alert_lvl, T1.strftime("%Y-%m-%dT%H:%M:%S"), T2.strftime("%Y-%m-%dT%H:%M:%S"))]
        mutt = mutt_base + mutt + ['--'] + MAILTO
        sub = subprocess.Popen(mutt, stdin=subprocess.PIPE)
        sub.communicate(summary)
        # send again without attachments if mutt had a problem (too many images)
        if sub.returncode != 0:
            mutt = mutt_base + ['--'] + MAILTO
            sub = subprocess.Popen(mutt, stdin=subprocess.PIPE)
            sub.communicate(summary)

    plt.close('all')
    del summary
    del mutt
