#! /usr/bin/env python

import sys, math
import numpy as np
import matplotlib.pyplot as plt
from obspy.core import read

def rekf1(dt, r, n, ein, sum):
    z = np.exp(dt)
    aus0 = r * ein[0]
    sum[0] = sum[0] + aus0
    for i in np.arange(1,n,1):
        aus0 = r * ein[i] + z * aus0
        sum[i] = sum[i] + aus0
    
    return sum

def rekf2(sre, sim, rre, rim, n, ein, sum):
    zabs = np.exp(sre)
    zre = zabs * np.cos(sim)
    zim = zabs * np.sin(sim)
    f0 = 2. * rre
    f1 = -2. * (rre * zre + rim * zim)
    g1 = 2. * zre
    g2 = -zabs**2
    aus0 = f0 * ein[0]
    sum[0] = sum[0] + aus0
    aus1 = aus0
    aus0 = f0 * ein[1] + f1 * ein[0] + g1 * aus1
    sum[1] = sum[1] + aus0

    for i in np.arange(2,n,1):
        aus2 = aus1
        aus1 = aus0
        aus0 = f0 * ein[i] + f1 * ein[i-1] + g1 * aus1 + g2 * aus2
        sum[i] = sum[i] + aus0

    return sum

# compute poles and zeros for the given subsystems

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

def politrend(mm,x,n):
#  remove polinomial trend
    y = x[:-1]
    ndi = 8
    m = min(mm,ndi-1)
    fnh = n / 2.
    c = np.empty((m+1,m+1),dtype=np.float64)
    b = np.empty(m+1,dtype=np.float64)
    h = np.empty(m+2,dtype=np.float64)
    imax = np.empty(ndi,dtype=np.float64)
    for l in xrange(0,m+1,1):
        for k in xrange(0,m+1,1):
#            d = np.arange(1,n+1,1, dtype=np.float64)
#            d /= fnh
#            d -= 1.0
#            d = d**(l+k)
#            c[l, k] += d.sum()
            for i in xrange(0,n,1):
                c[l, k] += (np.float64(i+1) / fnh - 1.)**(l+k)
#        d = np.arange(1,n+1,1, dtype=np.float64)
#        d /= fnh
#        d -= 1.0
#        d = d**l
#        d *= y
#        b[l] += d.sum()
        for i in xrange(0,n,1):      
            b[l] += (np.float64(i+1) / fnh - 1.)**(l) * x[i]
     
    a = np.linalg.solve(c,b)
    xpol = a[m]
    
    #for l in xrange(m,0,-1):
    #    d = np.arange(1,n+1,1, dtype=np.float64)
    #    d /= fnh
    #    d -= 1.0
    #    d += a[l-1]
    #    xpol *= d
       
    for i in xrange(0,n,1):
        for l in xrange(m,0,-1):
            xpol *= (np.float64(i+1) / fnh - 1.) + a[l-1]
        x[i] -= xpol
    return x

def ltisim(alias_on, data, delay, sub, til, sr, si, resid, residi, m0, m1, m2):
    sum = np.zeros(len(data))
    npts = len(data)
    tau = delay
    if tau > 0:
        tau = tau - dt

 # 1st order systems
    for l in np.arange(1,m1+1,1):
        i = m0 + l
        sum = rekf1(dt*sr[i],resid[i]*np.exp(-tau*sr[i]),npts,data,sum)
 # 2nd order systems
    for l in np.arange(1,m2+1,1):
        i = m0 + m1 + l
        if si[i] == 0.:
            sum = rekf1(dt*sr[i],resid[i]*np.exp(-tau*sr[i]),npts,data,sum)
            sum = rekf1(dt*sr[i+m2],resid[i+m2]*np.exp(-tau*sr[i+m2]),npts,data,sum)
        else:
            sre = -tau * sr[i]
            sim = -tau * si[i]
            zabs = np.exp(sre)
            zre = zabs * np.cos(sim)
            zim = zabs * np.sin(sim)
            rre = resid[i] * zre - residi[i] * zim
            rim = resid[i] * zim + residi[i] * zre
            sum = rekf2(dt*sr[i],dt*si[i],rre,rim,npts,data,sum)

    if alias_on == 0:    
        if delay > 0.:
            for i in np.arange(npts-1,0,-1):
                sum[i] = sum[i-1]

 # sum is now the output simulated with the system start parameters
 # Now you can correct for galvanic coupling or shaketable tilt
        sta = np.zeros(npts+1)

        if til != 0.:
            sta[0] = sum[ns1] / 2.
            for i in np.arange(1,npts,1):
                ii = i + 1
                sta[ii] = sta[ii-1] + (sum[i-1] + sum[i]) / 2.
            sta = politrend(1,sta,npts)
            suma = sta[0]
            sta[0] = suma / 2.
            for i in np.arange(1,npts,1):
                ii = i + 1
                sumn = sta[ii]
                sta[ii] = sta[ii-1] + (suma + sumn) / 2.
                suma = sumn
            sta = politrend(2,sta,npts)

        comp = til * 0.00981 * dt**2
        
        for i in np.arange(0,npts,1):
            ii = i + 1
            sum[i] = ausf[i] - sum[i] - sub * einf[i] + comp * sta[ii]
        for i in np.arange(0,npts,1):
            ii = i + 1
            sta[ii] = sum[i]
        sta = politrend(3,sta,npts)
        for i in np.arange(0,npts,1):
            ii = i + 1
            sum[i] = sta[ii]
        offset = 0.
        for i in np.arange(0,npts,1):
            offset = offset + sum[i]
        offset = offset / npts
        for i in np.arange(0,npts,1):
            sum[i] = sum[i] - offset

    return sum

            
######################################################################
st = read(sys.argv[1])
tr = st[0]
data = tr.data[6000:30000]
n = 24000
dt = 1/tr.stats.sampling_rate

st_ausf = read(sys.argv[2])
tr_ausf = st[0]
ausf = tr.data

st_einf = read(sys.argv[3])
tr_einf = st[0]
einf = tr.data

syspar = np.array([249.36727304704618, 12.566370614359172, 12.566370614359172, 0.38268343236508978, 0.92387953251128674])
m0 = 0
m1 = 0
m2 = 2

tau = 0.01
sr = np.zeros(m0+m1+2*m2+1)
si = np.zeros(m0+m1+2*m2+1)
resid = np.zeros(m0+m1+2*m2+1)
residi = np.zeros(m0+m1+2*m2+1)
sum = np.zeros(n)
alias_on = 0
delay = 0.
sub = 0.
til = 0.
freqDamp2paz(syspar,sr,si,resid,residi,m0,m1,m2)
ltisim(alias_on,data,delay,sub,til,sr,si,resid,residi,m0,m1,m2)

######################################################################
#fig = plt.figure()
#ax1 = plt.subplot(211)
#ax1.plot(tr.data)
#
#ax2 = plt.subplot(212)
#ax2.plot(sum)
#
#plt.show()
