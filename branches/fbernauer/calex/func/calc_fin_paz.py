#! /usr/bin/env python
 
import sys, math
import numpy as np

def def_sys_par(x0, dt, m0, m1, m2,\
                amp, delay, sub, til,\
                typ1, typ2,\
                corn_freqs1, corn_freqs2, dmp):
 #gain 
    gain = amp * dt
 #1st order
    for i in np.arange(0,m1,1):
        if typ1[i] == 'hp1':
            m0 = m0 + 1
        if typ1[i] == 'lp1':
            gain = gain * 2. * np.pi * corn_freqs1[i]

 #2nd order
    for i in np.arange(0,m2,1):
        if typ2[i] == 'hp2':
            m0 = m0 + 2
        if typ2[i] == 'bp2':
            m0 = m0 + 1
            gain = gain * 2. * np.pi * corn_freqs2[i]
        if typ2[i] == 'lp2':
            gain = gain * (2. * np.pi * corn_freqs2[i])**2

    for i in np.arange(0,m0,1):
        x0[i] = 0
    x0[m0] = gain
    for i in np.arange(0,m1,1):
        x0[m0+1+i] = 2. * np.pi * corn_freqs1[i]
    if m0 < 0:
        m0 = 0
        x0[m0] = gain
        for i in np.arange(0,m1,1):
            x0[1+i] = 2. * np.pi * corn_freqs1[i]
        m1 = m1 + 1
        x0[m1] = 0
    for i in np.arange(0,m2,1):
        x0[m0+m1+1+i] = 2. * np.pi * corn_freqs2[i]
        x0[m0+m1+m2+1+i] = dmp[i]

    return x0, m0, m1, m2

def freqDamp2paz(x0, sr, si, resid, residi, m0, m1, m2):
 #Poles
    for i in np.arange(1,m1+1,1):
        sr[m0+i] = -x0[m0+i]
        si[m0+i] = 0.

    for i in np.arange(1,m2+1,1):
        w = x0[m0+m1+i]
        h = x0[m0+m1+m2+i]
        wh = w * h
        whh = w * np.sqrt(1. - h**2)
        if h < 1:
            sr[m0+m1+i] = -wh
            si[m0+m1+i] = whh
            sr[m0+m1+m2+i] = -wh
            si[m0+m1+m2+i] = -whh
        else:
            sr[m0+m1+i] = -wh + whh
            si[m0+m1+i] = 0.
            sr[m0+m1+m2+i] = -wh - whh
            si[m0+m1+m2+i] = 0.
 #Zeros
    for i in np.arange(m0+1,m0+m1+2*m2+1,1):
        cresr = x0[0]
        cresi = 0.
        spowr = 1.
        spowi = 0.
        for k in np.arange(1,m0+1,1):
            spowre = spowr * sr[i] - spowi * si[i]
            spowi = spowr * si[i] + spowi * sr[i]
            spowr = spowre
            cresr = cresr + x0[k] * spowr
            cresi = cresi + x0[k] * spowi
        for k in np.arange(m0+1,m0+m1+2*m2+1,1):
            if k != i:
                 sdr = sr[i] - sr[k]
                 sdi = si[i] - si[k]
                 sdq = sdr * sdr + sdi * sdi
                 cresre = (cresr * sdr + cresi * sdi) / sdq
                 cresi = (cresi * sdr - cresr * sdi) / sdq
                 cresr = cresre
        resid[i] = cresr
        residi[i] = cresi

    return sr, si, resid, residi


syspar0 = np.zeros(30)
sr0 = np.zeros(30)
si0 = np.zeros(30)
resid0 = np.zeros(30)
residi0 = np.zeros(30)
amp = 2.062362e-02
delay = 0.
sub = 0.
til = 0.
corn_freqs2_fin = []
corn_freqs1_fin = [1.155896]
dmp_fin = [5.365856e-1]
dmp_fin = []
m0_sta = 0
m1_sta = 1
m2_sta = 0
typ2_sta = []
typ1_sta = ['lp1']
dt = 0.01
syspar, m0_fin, m1_fin, m2_fin = def_sys_par(syspar0, dt, m0_sta, m1_sta, m2_sta,\
                                             amp, delay, sub, til,\
                                             typ1_sta, typ2_sta,\
                                             corn_freqs1_fin, corn_freqs2_fin, dmp_fin)

sr, si, resid, residi = freqDamp2paz(syspar, sr0, si0, resid0, residi0, m0_fin, m1_fin, m2_fin)

print 'sr', sr
print 'si', si
print 'resid', resid 
print 'residi', residi

sr = sr[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
si = si[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
resid = resid[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
residi = residi[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
paz_file_name = 'pazfile'
paz_file = open(paz_file_name, 'w')
paz_file.write('poles:\n')
for i in range(len(sr)):
    paz_file.write(str(sr[i]) + ' + ' + '(' + str(si[i]) + 'j)\n')
paz_file.write('zeros:\n')
for i in range(len(resid)):
    paz_file.write(str(resid[i]) + ' + ' + '(' + str(residi[i]) + 'j)\n')

