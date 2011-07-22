#!/usr/bin/env python

import os
from obspy.core import Trace, UTCDateTime
import numpy as np


class Vol1Reader(object):
    def __init__(self,filename):
        self.fn = filename
        self.trace = self.read(filename)
    
    def read(self,fn):
        f = open(fn, 'r')
        smdict = {}
        f.readline()
        a = f.readline().split()
        latitude = float(a[2])+float(a[3])/60. +float(a[4][0:-1])/(60.*60.)
        longitude = float(a[5])+float(a[6])/60.+float(a[7][0:-1])/(60.*60.)
        smdict['lat'] = latitude
        smdict['lon'] = longitude
        smdict['site'] = a[1]
        smdict['site-name'] = f.readline().rstrip()
        smdict['instrument'] = f.readline().rstrip()
        f.readline()
        a = f.readline().split()
        site = a[1]
        for i in xrange(3): f.readline()
        npts = int(f.readline().split()[3])
        delta = float(f.readline().split()[-2])
        f.readline()
        comp = f.readline().split()[1]
        for i in xrange(3): f.readline()
        a = f.readline().split()
        year, month, day, hour, minute, sec = map(int,a[0:6])
        nsec, microsec = divmod(sec,10)
        microsec *= 1e5
        stats = {'network': '', 'delta': delta,
                 'station': site, 'location': '',
                 'starttime': UTCDateTime(year, month, day, hour, minute, nsec, int(microsec)),
                 'npts': npts, 'calib': 1.0,
                 'sampling_rate': 1./delta, 'channel': comp,'smdict':smdict}
        for i in xrange(9): f.readline()
        cnt = 0
        data = []
        while cnt < npts:
            a = f.readline().split()
            cnt += len(a)
            for _e in map(float,a):
                data.append(_e)
        
        data = np.array(data)
        tr = Trace(data,stats)
        return tr

if __name__ == '__main__':
    dirdat = r'H:\workspace\svn.obspy.org\branches\strong_motion'
    testfn = os.path.join(dirdat, 'O90400A1.V1A')
    v1 = Vol1Reader(testfn)
    v1.trace.plot() 
    print v1.trace.stats    
    
        
