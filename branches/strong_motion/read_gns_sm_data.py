"""
A python class to read Volume 1 and Volume 2 formatted strong motion data files
as used by the strong motion working group at GNS Science, New Zealand.
"""
import os
from obspy.core import Trace, UTCDateTime, Stream
import numpy as np

class Vol12Error(Exception): pass

class Vol12Reader(object):
    def __init__(self,filename):
        self.fn = filename
        self.f = open(self.fn, 'r')
        self.stream = Stream()
        for i in xrange(3):
            self.stream += self.read_comp(self.f)
        
    def read_comp(self,f):
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
        for i in xrange(6): f.readline()
        comp = f.readline().split()[1]
        for i in xrange(3): f.readline()
        a = f.readline().split()
        year, month, day, hour, minute, sec = map(int,a[0:6])
        nsec, microsec = divmod(sec,10)
        microsec *= 1e5
        for i in xrange(2):f.readline()
        a = map(int,f.readline().split())
        smdict['prepend'] = a[1]
        smdict['append'] = a[2]
        nptsa = a[3]
        nptsv = a[4]
        nptsd = a[5]
        listnpts = [nptsa,nptsv,nptsd]        
        for i in xrange(2): f.readline()
        a = map(float,f.readline().split())
        delta = a[5]
        for i in xrange(3): f.readline()
        st = Stream()
        for i,npts in enumerate(listnpts):
            if npts < 1: break
            stats = {'network': '', 'delta': delta,
                     'station': site, 'location': '',
                     'starttime': UTCDateTime(year, month, day, hour, minute, nsec, int(microsec)),
                     'npts': npts, 'calib': 1.0,
                     'sampling_rate': 1./delta, 'channel': comp,'smdict':smdict}
            cnt = 0
            data = []
            intv = 8
            while cnt < npts:
                a = f.readline()
                a = a.rstrip()
                old = 0
                while True:
                    val = a[old:old+intv]
                    if not val: break
                    if float(val) > 999999.:
                        data.append(0.)
                    else:
                        data.append(float(val))
                    cnt += 1
                    old += intv
            if cnt != npts: 
                raise Vol12Error("Number of samples in header inconsistent with number of samples in trace: %s"%self.fn)
            data = np.array(data)
            st.append(Trace(data,stats))
                
        return st

if __name__ == '__main__':
    import shutil
    dirdat = u'H:\workspace\svn.obspy.org\\branches\strong_motion'
    testfn = os.path.join(dirdat, 'O90400A1.V1A')
    testfn = os.path.join(dirdat,'19900210032700E_Vol2_O90400A1.V2A')
    #testfn = r's:\proc\2011\06_Prelim\2011-06-13_022049\Vol1\data\20110613_022049_CACS.v1a'
    testfn = '20110613_022049_CACS.v1a'
    #shutil.copy(testfn,dirdat)
    v1 = Vol12Reader(testfn)
    print v1.stream
    v1.stream.plot() 
    
        
