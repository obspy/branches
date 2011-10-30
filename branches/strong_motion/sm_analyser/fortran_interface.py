"""
Interface with the fortran code esvol2fm.f95 which 
computes Volume 2 files out of a list of Volume 1 files. 
"""

import os
import subprocess as sp
import re
from read_gns_sm_data import Vol12Reader, Vol12Error
from obspy.core import UTCDateTime

class FortranHandlerError(Exception): pass

class FortranHandler():
    """
    Main class to interface the Fortran program.
    """
    def __init__(self, bindir):
        self.inputfn = 'filt_special.dat'
        self.curdir = os.getcwd()
        os.chdir(bindir)
        if os.path.isfile(self.inputfn):
            self.dest = self.inputfn.replace('.dat', '_tmp.dat')
            if os.path.isfile(self.dest):
                raise FortranHandlerError("File %s already exists.\n \
                This could be the result of a previous run that crashed.\n \
                Please check the file %s and %s before you run this program again." % (self.dest, self.inputfn, self.dest))
            print "mv %s --> %s" % (self.inputfn, self.dest)
            os.rename(self.inputfn, self.dest)
        else:
            raise FortranHandlerError("Can't find %s.\n \
                Please make sure you provide this file in the same folder as the fortran executables.\n"\
                % (self.inputfn))
        self.cmd = 'esvol2m_special'
        self.pattern = re.compile(r'\d+\s+(s:\\[\w\\ -_.\d]*)')
        self.fin = open(self.dest, 'r')
        self.firstline = self.fin.readline()
        self.data = []
        for line in self.fin.readlines():
            # ignore commented lines
            if line.startswith('!'): continue
            self.data.append(line)
        self.counter = 0

    
    def __del__(self):
        if hasattr(self, 'fin'):
            self.fin.close()
        if hasattr(self, 'inputfn') and hasattr(self, 'dest'):
            if not os.path.isfile(self.inputfn) and os.path.isfile(self.dest):
                print "mv %s --> %s" % (self.dest, self.inputfn)
                os.rename(self.dest, self.inputfn)
        if hasattr(self, 'curdir'):
            os.chdir(self.curdir)

    def __call__(self):
        self.run_fortran()
        return self.v1, self.v2

    def get_filename(self,date,csite,fname):
        if csite == 'AVIS' or csite == 'BENS' or csite == 'MANS' \
        or csite == 'PKIS' or csite == 'TKAS' or csite == 'TUDS' \
        or csite == 'MTDS' or csite == 'MWDS' or csite == 'NZAS' \
        or csite == 'LPOC':
            csubd = 'S:\Power_company'
        else:
            csubd = 'S:\proc'
        dn = os.path.join(csubd,str(date.year),'%02d_Prelim'%date.month,
                          '%4d-%02d-%02d_%02d%02d%02d'%(date.year,date.month,date.day,date.hour,date.minute,date.second),
                          'Vol1','data')
        return os.path.join(dn,fname+'.V1A')

    def run_fortran(self):
        """
        Run the Fortran program esvol2m_special and read in the 
        resulting Volume 2 file as well as the source Volume 1 file.'
        """
        line = self.data[self.counter]
        a = line.split()
        fin = a[0]
        dt = a[6]
        t = a[7]
        date = UTCDateTime(int(dt[0:4]),int(dt[4:6]),int(dt[6:8]),int(t[0:2]),int(t[2:4]),int(t[4:6]))
        csite = fin.split('_')[-1] 
        if not os.path.isfile(self.get_filename(date,csite,fin)):
            raise FortranHandlerError("Can not find %s:" % fin)
        filtdat = open(self.inputfn, 'w')
        filtdat.writelines(line)
        filtdat.close()
        a = line.split()
        self.highp = [float(a[1]), float(a[2])]
        self.lowp = [float(a[3]), float(a[4])]
        self.startt = int(a[9])
        self.endt = int(a[10])
        self.dmn = int(a[11])
        self.dtrnd = int(a[12])
        p = sp.Popen([self.cmd], stdout=sp.PIPE).communicate()[0]
        for line in p.split('\n'):
            match = self.pattern.match(line.strip())
            if match is not None:
                vol1fn = match.group(1)
                path, fn = os.path.split(vol1fn)
                vol2fn = fn.replace('.v1a', '.V2A')
                self.v1 = Vol12Reader(vol1fn)
                self.v2 = Vol12Reader(vol2fn)
        os.remove(self.inputfn)
                    

if __name__ == '__main__': 
    import pylab as plt
    import numpy as np
    bindir = u'I:\SEISMO\yannikb\standard_processing\\fortran_stripped'
    test = FortranHandler(bindir=bindir)
    v1, v2 = test()
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    tr1 = v1.stream[0]
    t1 = np.arange(tr1.stats.npts) * tr1.stats.delta
    
    tr2 = v2.stream[0]
    nopre = tr2.stats.smdict.prepend
    noapp = tr2.stats.smdict.append
    tr2.data = tr2.data[nopre:tr2.stats.npts - noapp]
    tr2.stats.npts = tr2.data.size
    t2 = np.arange(tr2.stats.npts) * tr2.stats.delta
    ax1.plot(t1, tr1.data)
    ax2.plot(t2, tr2.data)
    plt.show()

