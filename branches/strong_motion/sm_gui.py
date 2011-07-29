from read_gns_sm_data import Vol12Reader
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure, rcParams
from obspy.core import Trace, UTCDateTime, Stream
import obspy.mseed
import Tkinter as Tk
import sys
import os
import numpy as np
from fortran_interface import *

rcParams['figure.subplot.hspace'] = 0.1 
rcParams['figure.subplot.bottom'] = 0.2
rcParams['xtick.labelsize'] = 8
rcParams['ytick.labelsize'] = 8
rcParams['legend.fontsize'] = 8

class FilterError(Exception): pass
 
class DataHandler(FortranHandler):
    def __init__(self):
        bindir = u'H:\workspace\svn.obspy.org\\branches\strong_motion\\fortran_stripped'
        FortranHandler.__init__(self, bindir=bindir)
        #self.dirdat = u"H:\workspace\svn.obspy.org\\branches\strong_motion"
    
    def getspectra(self):
        #testfn1 = os.path.join(self.dirdat, 'O90400A1.V1A')
        #v1 = Vol12Reader(testfn1)
        tr1 = self.v1.stream[0]
        tr2 = self.v1.stream[1]
        tr3 = self.v1.stream[2]
        fspec1 = np.fft.fft(tr1.data)
        fspec2 = np.fft.fft(tr2.data)
        fspec3 = np.fft.fft(tr3.data)
        freqs = np.fft.fftfreq(tr1.stats.npts, tr1.stats.delta)
        return fspec1, fspec2, fspec3, freqs
        
    def gettimeseries(self):
        #testfn2 = os.path.join(self.dirdat,'19900210032700E_Vol2_O90400A1.V2A')
        #v2 = Vol12Reader(testfn2)
        tr1 = self.v2.stream[2]
        tr2 = self.v2.stream[5]
        tr3 = self.v2.stream[8]
        time = np.arange(tr1.stats.npts) * tr1.stats.delta
        return tr1, tr2, tr3, time
    
class PlotIterator:
    def __init__(self):
        self.counter = 0

    def __iter__(self, index):
        return self
    
    def next(self):
        if self.counter < len(self.data) - 1:
            self.counter += 1
            self.update()
        
    def prev(self):
        if self.counter > 0:
            self.counter -= 1
            self.update()
            
    def onpress(self, event):
        if event.key == 'n':
            self.next()
        if event.key == 'p':
            self.prev()

   
class SmGui(DataHandler, PlotIterator):
    def __init__(self, parent):
        DataHandler.__init__(self)
        PlotIterator.__init__(self)
        ### Window setup
        self.root = parent
        self.entry_frame = Tk.Frame(root)
        self.entry_frame.pack(side='top', pady=20)
        self.figure_frame = Tk.Frame(root)
        self.figure_frame.pack(side='top', anchor='n', expand=1, fill=Tk.BOTH)
        self.left_frame = Tk.Frame(self.figure_frame)
        self.left_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.right_frame = Tk.Frame(self.figure_frame)
        self.right_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.root.wm_title("Strong motion analyser")
        self.f1 = Figure(figsize=(5., 5.), dpi=100)
        self.f2 = Figure(figsize=(6.4, 5.), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.f1, master=self.left_frame)
        self.canvas2 = FigureCanvasTkAgg(self.f2, master=self.right_frame)
        self.canvas1.show()
        self.canvas1.get_tk_widget().pack(side='left', expand=1, fill=Tk.BOTH) 
        self.canvas2.get_tk_widget().pack(side='left', expand=1, fill=Tk.BOTH) 
        toolbar = NavigationToolbar2TkAgg(self.canvas1, self.left_frame)
        toolbar.update()
        self.canvas1._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        toolbar1 = NavigationToolbar2TkAgg(self.canvas2, self.right_frame)
        toolbar1.update()
        self.canvas2._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        #self.highp = [0.25, 0.5]
        #self.lowp = [20., 30.]
        self.plotcanvas()

        self.p = {}
        self.p['hlow'] = Tk.DoubleVar();self.p['hlow'].set(self.highp[0])
        self.p['hhgh'] = Tk.DoubleVar();self.p['hhgh'].set(self.highp[1])
        self.p['llow'] = Tk.DoubleVar();self.p['llow'].set(self.lowp[0])
        self.p['lhgh'] = Tk.DoubleVar();self.p['lhgh'].set(self.lowp[1])

        self.textentry(self.entry_frame, self.p['hlow'], self.p['hhgh'], 'Highpass filter')
        #self.textentry(self.entry_frame, self.p['llow'], self.p['lhgh'], 'Low-pass filter')
        flt_button = Tk.Button(self.entry_frame, text='Enter', width=8, command=self.recalc)
        flt_button.pack(side='left', padx=20)
        p_button = Tk.Button(self.entry_frame, text='Previous', width=8, command=self.prev)
        p_button.pack(side='left', padx=10)
        n_button = Tk.Button(self.entry_frame, text='Next', width=8, command=self.next)
        n_button.pack(side='left', padx=10)


    def plotcanvas(self):
        self.run_fortran()
        self.plotspectra()
        self.plottimeseries()
        
    def textentry(self, parent, variable1, variable2, label):
        """Make a textentry field tied to variable."""
        # pack a label and entry horizontally in a frame:
        l = Tk.Label(parent, text=label)
        l.pack(side='left', expand=0, padx=20)
        widget = Tk.Entry(parent, textvariable=variable1, width=8)
        widget.pack(side='left', expand=0, padx=10)
        widget = Tk.Entry(parent, textvariable=variable2, width=8)
        widget.pack(side='left', expand=0, padx=10)
        return widget

    def plotspectra(self):
        fspec1, fspec2, fspec3, freqs = self.getspectra()
        ax1 = self.f1.add_subplot(3, 1, 1)
        ax2 = self.f1.add_subplot(3, 1, 2)
        ax3 = self.f1.add_subplot(3, 1, 3)
        ax1.loglog(freqs, abs(fspec1))
        ax2.loglog(freqs, abs(fspec2))
        ax3.loglog(freqs, abs(fspec3))
        ymin, ymax = ax1.get_ylim()
        ax1.vlines(self.highp[0], ymin, ymax)
        ax1.set_ylim(ymin, ymax)
        ymin, ymax = ax2.get_ylim()
        ax2.vlines(self.highp[0], ymin, ymax)
        ymin, ymax = ax3.get_ylim()
        ax3.vlines(self.highp[0], ymin, ymax)
        ax1.set_xlim(0.01, 20)
        ax2.set_xlim(0.01, 20)
        ax3.set_xlim(0.01, 20)
        ax1.set_xticks([])
        ax2.set_xticks([])
        ax3.set_xlabel('Frequency [Hz]')
    
    def plottimeseries(self):
        tr1, tr2, tr3, time = self.gettimeseries()
        ax1 = self.f2.add_subplot(3, 1, 1)
        ax2 = self.f2.add_subplot(3, 1, 2)
        ax3 = self.f2.add_subplot(3, 1, 3)
        ax1.plot(time, tr1.data, label=tr1.stats.channel)
        ax1.legend(loc='upper right')
        ax2.plot(time, tr2.data, label=tr2.stats.channel)
        ax2.legend(loc='upper right')
        ax3.plot(time, tr3.data, label=tr3.stats.channel)
        ax3.legend(loc='upper right')
        ax1.set_xticks([])
        ax2.set_xticks([])
        ax3.set_xlabel('Time [s]')
        ax1.set_title(tr1.stats.station)

    def update(self):
        self.f1.clf();self.f2.clf()
        self.plotcanvas()
        self.canvas1.draw()
        self.canvas2.draw()
        self.p['hlow'].set(self.highp[0])
        self.p['hhgh'].set(self.highp[1])
        self.p['llow'].set(self.lowp[0])
        self.p['lhgh'].set(self.lowp[1])

    def check_filterband(self):
        f1low = self.p['llow'].get()
        f2low = self.p['lhgh'].get()
        f1high = self.p['hlow'].get()
        f2high = self.p['hhgh'].get()
        tr = self.v1.stream[0]
        npts = tr.stats.npts
        dt = tr.stats.delta
        if f1low >= f2low:
            raise FilterError("%.2f has to be smaller than %.2f" % (f1low, f2low))
        if f1high >= f2high:
            raise FilterError("%.2f has to be smaller than %.2f" % (f1high, f2high))
        fnyq = 0.5 / dt
        nf = npts / 2 + 1
        fclow = (f1low + f2low) / 2.
        fchigh = (f1high + f2high) / 2.
        res = fnyq / float(nf - 1)
        dfl = f2low - f1low
        dfh = f2high - f1high
        if abs(dfl) <= res:
            raise FilterError("Filter transition bandwidth (%.2f) <= frequency resolution (%.2f)." % (abs(dfl), res))
        if abs(dfh) <= res:
            raise FilterError("Filter transition bandwidth (%.2f) <= frequency resolution (%.2f)." % (abs(dfh), res))
        print fclow, fchigh, 0.25 / dt + res
            
    def recalc(self):
        line = self.data[self.counter]
        a = line.split()
        nline = "%s%6.2f%6.2f%6.2f%6.2f" % (a[0], self.p['hlow'].get(), self.p['hhgh'].get(), \
                                                self.p['llow'].get(), self.p['lhgh'].get())
        idx = line.find(a[4]) + len(a[4])
        nline += line[idx::]
        print line
        print nline
        #self.data[self.counter] = nline
        try:
            self.check_filterband()
        except FilterError,e:
            print e
        else:
            self.update()     
            
root = Tk.Tk()               # root (main) window
smviz = SmGui(root)
root.mainloop()
