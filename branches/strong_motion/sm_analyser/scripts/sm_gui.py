"""
This is the main script which builds the GUI and 
thereby provides the user interface to the Fortran
program 'esvol2m_special'. 
"""

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure, rcParams
from obspy.core import Trace, UTCDateTime, Stream
import sys
import os
import numpy as np
from sm_analyser.fortran_interface import *
import Tix as Tk
from Tkconstants import *
import tkMessageBox
from tkFileDialog import asksaveasfilename, askdirectory

rcParams['figure.subplot.hspace'] = 0.1 
rcParams['figure.subplot.bottom'] = 0.2
rcParams['xtick.labelsize'] = 8
rcParams['ytick.labelsize'] = 8
rcParams['legend.fontsize'] = 8

class FilterError(Exception): pass
"""
Raised if the filter range input by the user is not
compliant with the Fortran program.
"""
 
class DataHandler(FortranHandler):
    """
    Return the spectra and time series of the filtered acceleration records, 
    the unfiltered acceleration records or the filtered displacement records. 
    """
    
    def __init__(self, bindir):
        FortranHandler.__init__(self, bindir=bindir)
    
    def getspectra(self, choices, spec_old):
        """
        Compute the fft and return the spectra and their corresponding frequencies.
        """
        idx = choices.index(spec_old)
        if idx == 0:
            tr1 = self.v2.stream[2]
            tr2 = self.v2.stream[5]
            tr3 = self.v2.stream[8]
        if idx == 1:
            tr1 = self.v2.stream[0]
            tr2 = self.v2.stream[3]
            tr3 = self.v2.stream[6]
        if idx == 2:
            tr1 = self.v1.stream[0]
            tr2 = self.v1.stream[1]
            tr3 = self.v1.stream[2]
        fspec1 = np.fft.fft(tr1.data)
        fspec2 = np.fft.fft(tr2.data)
        fspec3 = np.fft.fft(tr3.data)
        freqs = np.fft.fftfreq(tr1.stats.npts, tr1.stats.delta)
        return fspec1, fspec2, fspec3, freqs
        
    def gettimeseries(self, choices, hist_old):
        """
        Return the timeseries.
        """
        idx = choices.index(hist_old)
        if idx == 0:
            tr1 = self.v2.stream[2]
            tr2 = self.v2.stream[5]
            tr3 = self.v2.stream[8]
        if idx == 1:
            tr1 = self.v2.stream[0]
            tr2 = self.v2.stream[3]
            tr3 = self.v2.stream[6]
        if idx == 2:
            tr1 = self.v1.stream[0]
            tr2 = self.v1.stream[1]
            tr3 = self.v1.stream[2]
            
        time = np.arange(tr1.stats.npts) * tr1.stats.delta
        return tr1, tr2, tr3, time
    
class PlotIterator:
    """
    This is an Iterator class to go through the list of filenames.
    """
    
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
    """
    This is the main class which constructs the GUI and calls the plotting routines.
    """
    def __init__(self, parent, bindir):
        self.bindir = bindir
        self.choices_ts = ['Displacement (filtered)', 'Acceleration (filtered)',
                        'Acceleration (unfiltered)']
        self.hist_old = self.choices_ts[0]
        self.spec_old = self.choices_ts[2]
        self.p = {} # dictionary to hold all Tk variables
        self.p['pmax'] = Tk.IntVar(); self.p['pmax'].set(0)
        self.p['fltrng'] = Tk.IntVar(); self.p['fltrng'].set(1)
        ### Window setup
        self.root = parent
        self.entry_frame = Tk.Frame(root)
        self.entry_frame.pack(side='top', pady=5)
        self.figure_frame = Tk.Frame(root)
        self.figure_frame.pack(side='top', anchor='n', expand=1, fill=Tk.BOTH)
        self.left_frame = Tk.Frame(self.figure_frame)
        self.left_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.right_frame = Tk.Frame(self.figure_frame)
        self.right_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.root.wm_title("Strong motion analyser")
        if self.bindir is None:
            self.choose_bin_directory()
        if self.bindir == '':
            sys.exit()
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

        DataHandler.__init__(self, self.bindir)
        PlotIterator.__init__(self)

        # Make initial plot of first record
        self.plotcanvas()

        # set number of points variable
        self.p['npts'] = Tk.IntVar(); self.p['npts'].set(self.npts)

        # set filter to default filter
        self.p['hlow'] = Tk.DoubleVar();self.p['hlow'].set(self.highp[0])
        self.p['hhgh'] = Tk.DoubleVar();self.p['hhgh'].set(self.highp[1])
  
        # setting up radio buttons
        maxb = Tk.Checkbutton(self.entry_frame, text='Max', command=self.plotmax, 
                              variable=self.p['pmax'],indicatoron=0,width=4)
        maxb.pack(side='left')
        balmaxb = Tk.Balloon(self.entry_frame)
        balmaxb.bind_widget(maxb,balloonmsg='Plot maxima of timeseries.') 

        fltrng = Tk.Checkbutton(self.entry_frame, text='Flt', command=self.plotfltrng, 
                                variable=self.p['fltrng'],indicatoron=0,width=4)
        fltrng.pack(side='left')
        balfltrng = Tk.Balloon(self.entry_frame)
        balfltrng.bind_widget(fltrng,balloonmsg='Plot cutoff and corner frequencies of highpass filter.') 

        
        # setting up spin box for trimming
        trim_cntrl = Tk.Control(self.entry_frame, label='npts',integer=True, step=100,
                                 variable=self.p['npts'])
        trim_cntrl.pack(side='left', padx=5)
        # setting up trim button
        trim_button = Tk.Button(self.entry_frame, text='Trim', width=8, command=self.recalc)
        trim_button.pack(side='left', padx=10)
    
        # setting up spin boxes for filtering
        hp_cntrl_lw = Tk.Control(self.entry_frame, label='cutoff', max=10, min=0, integer=False, step=0.01,
                                 variable=self.p['hlow'])
        hp_cntrl_lw.pack(side='left', padx=5)
        hp_cntrl_hg = Tk.Control(self.entry_frame, label='corner', max=10, min=0, integer=False, step=0.01,
                                 variable=self.p['hhgh'])
        hp_cntrl_hg.pack(side='left', padx=5)

        # setting up filter button
        flt_button = Tk.Button(self.entry_frame, text='Filter', width=8, command=self.recalc)
        flt_button.pack(side='left', padx=10)
        
        
        # setting up combo box for spectra
        spec_box = Tk.ComboBox(self.entry_frame, label='Spectra', editable=False, dropdown=True,
                               command=self.choose_spec, value=self.choices_ts[2])
        spec_box.insert('end', self.choices_ts[0])
        spec_box.insert('end', self.choices_ts[1])
        spec_box.insert('end', self.choices_ts[2])
        spec_box.pack(side='left', padx=10)

        # setting up combo box for timeseries
        hist_box = Tk.ComboBox(self.entry_frame, label='Timeseries', editable=False, dropdown=True,
                               command=self.choose_ts, value=self.choices_ts[0])
        hist_box.insert('end', self.choices_ts[0])
        hist_box.insert('end', self.choices_ts[1])
        hist_box.insert('end', self.choices_ts[2])
        hist_box.pack(side='left', padx=10)

        # setting up navigation and save button
        p_button = Tk.Button(self.entry_frame, text='Previous', width=8, command=self.prev)
        p_button.pack(side='left', padx=10)
        n_button = Tk.Button(self.entry_frame, text='Next', width=8, command=self.next)
        n_button.pack(side='left', padx=10)
        n_button = Tk.Button(self.entry_frame, text='Save', width=8, command=self.savefile)
        n_button.pack(side='left', padx=10)
        
    def plotmax(self):
        """
        Function called by 'Max' radio button
        """
        self.f2.clf()
        self.plottimeseries()
        self.canvas2.draw()
        
    def plotfltrng(self):
        """
        Function called by 'Flt' radio button
        """
        self.f1.clf()
        self.plotspectra()
        self.canvas1.draw()
        
    def choose_ts(self, value):
        """
        Choose timeseries to display; called by combo box 'hist_box'
        """    
        if value != self.hist_old:
            self.hist_old = value
            self.f2.clf()
            self.plottimeseries()
            self.canvas2.draw()
        else:
            pass
        
    def choose_spec(self, value):
        """
        Choose spectra to display. Called by the combo box 'spec box'
        """    
        if value != self.spec_old:
            self.spec_old = value
            self.f1.clf()
            self.plotspectra()
            self.canvas1.draw()
        else:
            pass
        
    def choose_bin_directory(self):
        """
        If the path to the directory holding the Fortran programs
        and the input file is not given on the command line this 
        function is called. It allows to choose the directory using a 
        directory browser before the program starts. 
        """
        self.bindir = askdirectory()
        while True:
            if self.bindir == '': break
            if os.path.isdir(self.bindir):
                if os.path.isfile(os.path.join(self.bindir, 'esvol2m.exe')) or \
                    os.path.isfile(os.path.join(self.bindir, 'esvol2m_special.exe')):
                    print "Fortran executable found in ", self.bindir
                    break
                else:
                    print "Can't find fortran executable %s or %s in specified directory" % ('esvol2m', 'esvol2m_special')
                    print "Please try again"
                    self.bindir = askdirectory()
            else:
                print "Directory %s does not exist" % (self.bindir)
                self.bindir = askdirectory()
                
    def savefile(self):
        """
        Function to save the modified filelist; called by the 'Save' button.
        """
        filename = asksaveasfilename(filetypes=[("allfiles", "*")])
        if filename == '':
            print "no filename given"
        else:
            print "saving %s" % filename
            f = open(filename, 'w')
            f.writelines(self.data)
            f.close()

    def plotcanvas(self):
        """
        Routine called everytime the fortran program needs to be run.
        """
        self.run_fortran()
        self.plotspectra()
        self.plottimeseries()
        
    def plotspectra(self):
        """
        Plot the spectra using Matplotlib.
        """
        fspec1, fspec2, fspec3, freqs = self.getspectra(self.choices_ts, self.spec_old)
        ax1 = self.f1.add_subplot(3, 1, 1)
        ax2 = self.f1.add_subplot(3, 1, 2, sharex=ax1)
        ax3 = self.f1.add_subplot(3, 1, 3, sharex=ax1)
        ax1.loglog(freqs, abs(fspec1))
        ax2.loglog(freqs, abs(fspec2))
        ax3.loglog(freqs, abs(fspec3))
        if self.p['fltrng'].get():
            ymin, ymax = ax1.get_ylim()
            ax1.vlines(self.highp[0], ymin, ymax)
            ax1.vlines(self.highp[1], ymin, ymax)
            ax1.set_ylim(ymin, ymax)
            ymin, ymax = ax2.get_ylim()
            ax2.vlines(self.highp[0], ymin, ymax)
            ax2.vlines(self.highp[1], ymin, ymax)
            ax2.set_ylim(ymin, ymax)
            ymin, ymax = ax3.get_ylim()
            ax3.vlines(self.highp[0], ymin, ymax)
            ax3.vlines(self.highp[1], ymin, ymax)
            ax3.set_ylim(ymin, ymax)
        ax1.set_xlim(0.01, 20)
        ax2.set_xlim(0.01, 20)
        ax3.set_xlim(0.01, 20)
        ax1.set_xticklabels(ax1.get_xticks(), visible=False)
        ax2.set_xticklabels(ax2.get_xticks(), visible=False)
        ax3.set_xlabel('Frequency [Hz]')
    
    def plottimeseries(self):
        """
        Plot the timeseries using Matplotlib.
        """
        tr1, tr2, tr3, time = self.gettimeseries(self.choices_ts, self.hist_old)
        ax1 = self.f2.add_subplot(3, 1, 1)
        ax2 = self.f2.add_subplot(3, 1, 2, sharex=ax1)
        ax3 = self.f2.add_subplot(3, 1, 3, sharex=ax1)
        ax1.plot(time, tr1.data, label=tr1.stats.channel)
        ax1.legend(loc='upper right')
        ax2.plot(time, tr2.data, label=tr2.stats.channel)
        ax2.legend(loc='upper right')
        ax3.plot(time, tr3.data, label=tr3.stats.channel)
        ax3.legend(loc='upper right')
        if self.p['pmax'].get():
            idmax1 = abs(tr1.data).argmax()
            max1 = tr1.data[idmax1]
            ax1.plot(idmax1*tr1.stats.delta,max1,'ro')
            idmax2 = abs(tr2.data).argmax()
            max2 = tr2.data[idmax2]
            ax2.plot(idmax2*tr2.stats.delta,max2,'ro')
            idmax3 = abs(tr3.data).argmax()
            max3 = tr3.data[idmax3]
            ax3.plot(idmax3*tr3.stats.delta,max3,'ro')
        ax1.set_xticklabels(ax1.get_xticks(), visible=False)
        ax2.set_xticklabels(ax2.get_xticks(), visible=False)
        ax3.set_xlabel('Time [s]')
        ymax = abs(tr1.data).max()
        ymax += 0.1 * ymax
        ax1.set_ylim(-ymax,ymax)
        ymax = abs(tr2.data).max()
        ymax += 0.1 * ymax
        ax2.set_ylim(-ymax,ymax)
        ymax = abs(tr3.data).max()
        ymax += 0.1 * ymax
        ax3.set_ylim(-ymax,ymax)
        ax1.set_title(tr1.stats.station)

    def update(self):
        """
        This function is called when the filter parameter or the length of the 
        time series changes.
        """
        self.f1.clf();self.f2.clf()
        self.plotcanvas()
        self.canvas1.draw()
        self.canvas2.draw()
        self.p['hlow'].set(self.highp[0])
        self.p['hhgh'].set(self.highp[1])

    def check_filterband(self):
        """
        Make some checks before passing the filter parameters to the Fortran program.
        """
        f1high = self.p['hlow'].get()
        f2high = self.p['hhgh'].get()
        tr = self.v1.stream[0]
        npts = tr.stats.npts
        dt = tr.stats.delta
        if f1high >= f2high:
            raise FilterError("%.2f has to be smaller than %.2f" % (f1high, f2high))
        fnyq = 0.5 / dt
        nf = npts / 2 + 1
        fchigh = (f1high + f2high) / 2.
        res = fnyq / float(nf - 1)
        dfh = f2high - f1high
        if abs(dfh) <= res:
            raise FilterError("Filter transition bandwidth (%.2f) <= frequency resolution (%.2f)." % (abs(dfh), res))
            
    def recalc(self):
        """
        Construct a new input line to the Fortran program from the user input for filter range and length of the 
        time series.
        """
        line = self.data[self.counter]
        a = line.split()
        nline = "%s%6.2f%6.2f" % (a[0], self.p['hlow'].get(), self.p['hhgh'].get())
        idx1 = line.find(a[2]) + len(a[2])
        idx2 = line.find(a[9]) + len(a[9]) - 12
        idx3 = idx2 + 12
        nline += line[idx1:idx2]
        nline += "%12d"%self.p['npts'].get()
        nline += line[idx3::]
        print line
        print nline
        self.data[self.counter] = nline
        try:
            self.check_filterband()
        except FilterError, e:
            print e
        else:
            self.update()     


            
if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("", "--fdir", dest="fdir",
                      help="Path to directory holding the Fortran standard processing executables and the 'filt.dat' file.",
                      default=None)
    (opts, args) = parser.parse_args()
    root = Tk.Tk()               # root (main) window
    smviz = SmGui(root, opts.fdir)
    root.mainloop()