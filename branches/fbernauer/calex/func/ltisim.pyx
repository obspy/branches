import sys, math
import numpy as np
cimport numpy as np
from obspy.core import read
from def_sys_par import def_sys_par
from freqDamp2paz import freqDamp2paz
from rekf1 import rekf1
from rekf2 import rekf2
from politrend import politrend

# simulate LTI system: 

def ltisim(alias_on,\
           np.ndarray[np.float64_t, ndim=1] data,\
           np.ndarray[np.float64_t, ndim=1] ausf,\
           np.ndarray[np.float64_t, ndim=1] einf,\
           double delay, double sub, double til,\
           np.ndarray[np.float64_t, ndim=1] sr,\
           np.ndarray[np.float64_t, ndim=1] si,\
           np.ndarray[np.float64_t, ndim=1] resid,\
           np.ndarray[np.float64_t, ndim=1] residi,\
           int m0, int m1, int m2,\
           double dt, int npts):
#def ltisim(alias_on,\
#           np.ndarray[np.float64_t, ndim=1] data,\
#           np.ndarray[np.float64_t, ndim=1] ausf,\
#           np.ndarray[np.float64_t, ndim=1] einf,\
#           double delay, double sub, double til,\
#           sr, si, resid, residi,\
#           int m0, int m1, int m2,\
#           double dt, int npts):
    cdef Py_ssize_t i, l
#    cdef double sre, sim, zabs, zre, zim, rre, rim
    cdef double comp, suma, sumn, offset, tau
    cdef np.ndarray[np.float64_t, ndim=1] sum = np.zeros(len(data))
    cdef np.ndarray[np.float64_t, ndim=1] sta = np.zeros(npts+1)
    tau = delay
    if tau > 0:
        tau = tau - dt

 # 1st order systems
    for l in xrange(1,m1+1,1):
        i = m0 + l
        sum = rekf1(dt*sr[i], resid[i]*np.exp(-tau*sr[i]), npts, data, sum)
 # 2nd order systems
    for l in xrange(1,m2+1,1):
        i = m0 + m1 + l
        if si[m0+m1+l] == 0.:
            sum = rekf1(dt*sr[i], resid[i]*np.exp(-tau*sr[i]), npts, data, sum)
            sum = rekf1(dt*sr[i+m2], resid[i+m2]*np.exp(-tau*sr[i+m2]), npts, data, sum)
        else:
            sre = -tau * sr[i]
            sim = -tau * si[i]
            zabs = np.exp(sre)
            zre = zabs * np.cos(sim)
            zim = zabs * np.sin(sim)
            rre = resid[i] * zre - residi[i] * zim
            rim = resid[i] * zim + residi[i] * zre
            sum = rekf2(dt*sr[i], dt*si[i], rre, rim, npts, data, sum)

    if alias_on == 0:    
        if delay > 0.:
            for i in xrange(npts-1,0,-1):
                sum[i] = sum[i-1]

 # sum is now the output simulated with the system start parameters
 # Now you can correct for galvanic coupling or shaketable tilt
#        sta = np.zeros(npts+1)

        if til != 0.:
            sta[0] = sum[0] / 2.
            for i in xrange(1,npts,1):
                sta[i+1] = sta[i] + (sum[i-1] + sum[i]) / 2.
            sta = politrend(1,sta,npts)
            suma = sta[0]
            sta[0] = suma / 2.
            for i in xrange(1,npts,1):
                sumn = sta[i+1]
                sta[i+1] = sta[i] + (suma + sumn) / 2.
                suma = sumn
            sta = politrend(2,sta,npts)

        comp = til * 0.00981 * dt**2
        
        for i in xrange(0,npts,1):
            sum[i] = ausf[i] - sum[i] - sub * einf[i] + comp * sta[i+1]
        for i in xrange(0,npts,1):
            sta[i+1] = sum[i]
        sta = politrend(3,sta,npts)
        for i in xrange(0,npts,1):
            sum[i] = sta[i+1]
#        offset = 0.
#        for i in xrange(0,npts,1):
#            offset = offset + sum[i]
#        offset = offset / npts
        offset = sum.sum() / npts
#        for i in xrange(0,npts,1):
#            sum[i] = sum[i] - offset
        sum = sum - offset

    return sum
