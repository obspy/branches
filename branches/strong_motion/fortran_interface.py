"""
Interface with the fortran code esvol2fm.f95 which 
computes Volume 2 files out of a list of Volume 1 files. 
"""

import os
import shutil
import subprocess as sp
import re
from read_gns_sm_data import Vol12Reader

class FortranHandlerError(Exception): pass

class FortranHandler():
    def __init__(self,bindir):
        self.inputfn = 'filt.dat'
        self.curdir = os.getcwd()
        os.chdir(bindir)
        if os.path.isfile(self.inputfn):
            self.dest = self.inputfn.replace('.dat','_tmp.dat')
            if os.path.isfile(self.dest):
                raise FortranHandlerError("File %s already exists.\n \
                This could be the result of a previous run that crashed.\n \
                Please check the file %s and %s before you run this program again."%(self.dest,self.inputfn,self.dest))
            print "copy %s --> %s"%(self.inputfn,self.dest)
            shutil.copy(self.inputfn,self.dest)
        else:
            raise FortranHandlerError("Can't find %s.\n \
                Please make sure you provide this file in the same folder as the fortran executables.\n"\
                %(self.inputfn))
        self.cmd = 'esvol2m'
        self.pattern = re.compile(r'\d+\s+(s:\\[\w\\ -_.\d]*)')
        self.fin = open(self.dest,'r')
        self.data = self.fin.readlines()
        self.counter = 0

    
    def __del__(self):
        if hasattr(self,'fin'):
            self.fin.close()
        if not os.path.isfile(self.inputfn):
            print "mv %s --> %s"%(self.dest,self.inputfn)
            os.rename(self.dest,self.inputfn)
        os.chdir(self.curdir)

    def __call__(self):
        self.run_fortran()
        return self.v1, self.v2
        
    def run_fortran(self):
        line = self.data[self.counter]
        filtdat = open(self.inputfn,'w')
        filtdat.writelines(line)
        filtdat.close()
        a = line.split()
        self.highp = [float(a[1]),float(a[2])]
        self.lowp = [float(a[3]),float(a[4])]
        p = sp.Popen([self.cmd],stdout=sp.PIPE).communicate()[0]
        for line in p.split('\n'):
            match = self.pattern.match(line.strip())
            if match is not None:
                vol1fn = match.group(1)
                if not os.path.isfile(vol1fn):
                    raise FortranHandlerError("Can not find %s:"%vol1fn)
                path,fn = os.path.split(vol1fn)
                vol2fn = fn.replace('.v1a','.V2A')
                if not os.path.isfile(vol2fn):
                    raise FortranHandlerError("Can not find %s:"%vol2fn)
                self.v1 = Vol12Reader(vol1fn)
                self.v2 = Vol12Reader(vol2fn)
        os.remove(self.inputfn)
                    

if __name__ == '__main__': 
    import pylab as plt
    import numpy as np
    bindir = u'H:\workspace\svn.obspy.org\\branches\strong_motion\\fortran_stripped'
    test = FortranHandler(bindir=bindir)
    v1,v2 = test()
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
    tr1 = v1.stream[0]
    t1 = np.arange(tr1.stats.npts)*tr1.stats.delta
    
    tr2 = v2.stream[0]
    nopre = tr2.stats.smdict.prepend
    noapp = tr2.stats.smdict.append
    tr2.data = tr2.data[nopre:tr2.stats.npts-noapp]
    tr2.stats.npts = tr2.data.size
    t2 = np.arange(tr2.stats.npts)*tr2.stats.delta
    ax1.plot(t1,tr1.data)
    ax2.plot(t2,tr2.data)
    plt.show()

