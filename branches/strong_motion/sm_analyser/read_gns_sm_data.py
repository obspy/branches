"""
A python class to read Volume 1 and Volume 2 formatted strong motion data files
as used by the strong motion working group at GNS Science, New Zealand.
"""
import os
from obspy.core import Trace, UTCDateTime, Stream
import numpy as np

class Vol12Error(Exception): pass
"""
Raised if inconsistencies in the file reading occur.
"""

class Vol12Reader(object):
    """
    Main class containing the routines to read Volume 1 and Volume 2 records.
    """
    def __init__(self,filename,headonly=False):
        if not os.path.isfile(filename):
            raise Vol12Error("Can't find file %s."%filename)
        self.fn = filename
        self.f = open(self.fn, 'r')
        self.stream = Stream()
        self.headonly = headonly
        for i in xrange(3):
            self.stream += self.read_comp(self.f)
        
    def read_comp(self,f):
        """
        Read all time series for one sensor orientation. Can be called several 
        times to read data from all three sensor orientations.
        """
        smdict = {}
        # read alphanumeric header
        f.readline()#skip one line
        a = f.readline().split()
        latitude = float(a[2])+float(a[3])/60. +float(a[4][0:-1])/(60.*60.)
        longitude = float(a[5])+float(a[6])/60.+float(a[7][0:-1])/(60.*60.)
        smdict['lat'] = latitude
        smdict['lon'] = longitude
        smdict['site'] = a[1]
        smdict['site-name'] = f.readline().rstrip()
        smdict['instrument'] = f.readline().rstrip()
        f.readline()#skip one line
        a = f.readline().split()
        site = a[1]
        for i in xrange(6): f.readline()#skip six lines
        comp = f.readline().split()[1]
        for i in xrange(3): f.readline()#skip three lines
        # read integer header
        a = f.readline().split()
        year, month, day, hour, minute, sec = map(int,a[0:6])
        nsec, microsec = divmod(sec,10)
        microsec *= 1e5
        f.readline() #skip one line
        a = map(int,f.readline().split())
        smdict['lilax'] = a[-4]
        smdict['compdir'] = a[-3]
        a = map(int,f.readline().split())
        smdict['prepend'] = a[1]
        smdict['append'] = a[2]
        nptsa = a[3]
        nptsv = a[4]
        nptsd = a[5]
        listnpts = [nptsa,nptsv,nptsd]
        # read floating-point header        
        for i in xrange(2): f.readline() #skip two lines
        a = map(float,f.readline().split())
        delta = a[5]
        for i in xrange(3): f.readline() #skip three lines
        st = Stream()
        for i,npts in enumerate(listnpts):
            if npts < 1: break
            stats = {'network': '', 'delta': delta,
                     'station': site, 'location': '',
                     'starttime': UTCDateTime(year, month, day, hour, minute, nsec, int(microsec)),
                     'npts': npts, 'calib': 1.0,
                     'sampling_rate': 1./delta, 'channel': comp,'smdict':smdict}
            if self.headonly:
                # number of full lines
                nl = npts/10
                # number of remaining entries in last line
                nr = npts%10
                # one full line contains 80 characters plus the end-of-line character
                f.read(nl*(10*8+1))
                f.read(nr*8+1)
                st.append(Trace(header=stats))
            else:
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
    pass    
        
