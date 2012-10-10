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
import math as m
from sm_analyser.fortran_interface import *
from sm_analyser.read_gns_sm_data import Vol12Reader
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
        try:
            FortranHandler.__init__(self, bindir=bindir)
        except FortranHandlerError, e:
            if tkMessageBox.showerror(title='Error', message=e):
                self.root.destroy()
                sys.exit()
            
        self.specs = {0:None, 1:None, 2:None}

    def ftransform(self, tr1, tr2, tr3):
        traces = [tr1,tr2,tr3]
        fspecs = []
        # check for zero traces
        for tr in traces:
            if np.size(np.nonzero(tr.data)) < 1:
                fspecs.append(np.ones(tr.data.size))
            else:
                fspecs.append(np.fft.fft(tr.data))
        freqs = np.fft.fftfreq(tr1.stats.npts, tr1.stats.delta)
        return fspecs[0], fspecs[1], fspecs[2], freqs
        
    def getspectra(self, choices, spec_old):
        """
        Compute the fft and return the spectra and their corresponding frequencies.
        """
        if self.v1.stream[0].stats.station == 'No data available':
            npts = self.v1.stream[0].stats.npts
            data = np.ones(npts)
            fspec1 = data[:]
            fspec2 = data[:]
            fspec3 = data[:]
            freqs = np.linspace(0.01, 20, npts) 
            return fspec1, fspec2, fspec3, freqs
        
        idx = choices.index(spec_old)
        if idx == 0:
            if self.specs[idx] is None:
                tr1 = self.v2.stream[2]
                tr2 = self.v2.stream[5]
                tr3 = self.v2.stream[8]
                self.specs[idx] = self.ftransform(tr1, tr2, tr3) 
        if idx == 1:
            if self.specs[idx] is None:
                tr1 = self.v2.stream[0]
                tr2 = self.v2.stream[3]
                tr3 = self.v2.stream[6]
                self.specs[idx] = self.ftransform(tr1, tr2, tr3) 
        if idx == 2:
            if self.specs[idx] is None:
                tr1 = self.v1.stream[0]
                tr2 = self.v1.stream[1]
                tr3 = self.v1.stream[2]
                self.specs[idx] = self.ftransform(tr1, tr2, tr3) 
        return self.specs[idx]
        
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
        self.root = parent
        self.bindir = bindir
        self.choices_ts = ['Displacement (filtered)', 'Acceleration (filtered)',
                        'Acceleration (unfiltered)']
        self.hist_old = self.choices_ts[0]
        self.spec_old = self.choices_ts[1]
        self.p = {} # dictionary to hold all Tk variables
        self.p['pmax'] = Tk.IntVar(); self.p['pmax'].set(0)
        self.p['fltrng'] = Tk.IntVar(); self.p['fltrng'].set(1)
        self.p['cutrng'] = Tk.IntVar(); self.p['cutrng'].set(1)
        self.p['pltlog2'] = Tk.IntVar(); self.p['pltlog2'].set(0)
        self.p['pltgrid'] = Tk.IntVar(); self.p['pltgrid'].set(1)
        if self.bindir is None:
            self.choose_bin_directory()
        if self.bindir == '':
            sys.exit()

        ### Window layout setup
        self.root = parent
        self.entry_frame = Tk.Frame(root)
        self.entry_frame.pack(side='top', pady=5)
        self.eq_frame = Tk.Frame(root, borderwidth=2, relief='sunken')
        self.eq_frame.pack(side='top', fill=Tk.BOTH, expand=0)
        self.figure_frame = Tk.Frame(root)
        self.figure_frame.pack(side='top', anchor='n', expand=1, fill=Tk.BOTH)
        self.left_frame = Tk.Frame(self.figure_frame)
        self.left_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.right_frame = Tk.Frame(self.figure_frame)
        self.right_frame.pack(side='left', anchor='n', expand=1, fill=Tk.BOTH)
        self.nav_frame = Tk.Frame(self.figure_frame)
        self.nav_frame.pack(side='right', anchor='center', expand=0, fill='none')
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

        DataHandler.__init__(self, self.bindir)
        PlotIterator.__init__(self)

        # Make initial plot of first record
        self.plotcanvas()

        # set line length of input file; needed to add comments to line
        # set number of points variable
        self.p['starttrim'] = Tk.IntVar(); self.p['starttrim'].set(self.startt)
        self.p['endtrim'] = Tk.IntVar(); self.p['endtrim'].set(self.endt)
        self.p['demean'] = Tk.IntVar(); self.p['demean'].set(self.dmn)
        self.p['detrend'] = Tk.IntVar(); self.p['detrend'].set(self.dtrnd)

        # set filter to default filter
        self.p['hlow'] = Tk.DoubleVar();self.p['hlow'].set(self.highp[0])
        self.p['hhgh'] = Tk.DoubleVar();self.p['hhgh'].set(self.highp[1])
  

        
        # setting up spin boxes for cutting
        trim_cntrl_st = Tk.Control(self.entry_frame, label='start', integer=True, step=1,
                                 variable=self.p['starttrim'])
        trim_cntrl_st.entry.config(font=10)
        trim_cntrl_st.label.config(font=10)
        trim_cntrl_st.pack(side='left', padx=5)
        
        trim_cntrl_ed = Tk.Control(self.entry_frame, label='end', integer=True, step=1,
                                 variable=self.p['endtrim'])
        trim_cntrl_ed.entry.config(font=10)
        trim_cntrl_ed.label.config(font=10)
        trim_cntrl_ed.pack(side='left', padx=5)

        # setting up trim button
        trim_button = Tk.Button(self.entry_frame, text='Cut', width=8, command=self.recalc, font=10)
        trim_button.pack(side='left', padx=10)
        
    
        # setting up spin boxes for filtering
        hp_cntrl_lw = Tk.Control(self.entry_frame, label='cutoff', max=10, min=0, integer=False, step=0.01,
                                 variable=self.p['hlow'])
        hp_cntrl_lw.entry.config(font=10)
        hp_cntrl_lw.label.config(font=10)
        hp_cntrl_lw.pack(side='left', padx=5)
        hp_cntrl_hg = Tk.Control(self.entry_frame, label='corner', max=10, min=0, integer=False, step=0.01,
                                 variable=self.p['hhgh'])
        hp_cntrl_hg.entry.config(font=10)
        hp_cntrl_hg.label.config(font=10)
        hp_cntrl_hg.pack(side='left', padx=5)

        # setting up filter button
        flt_button = Tk.Button(self.entry_frame, text='Filter', width=8, command=self.recalc, font=10)
        flt_button.pack(side='left', padx=10)
        
        
        # setting up combo box for spectra
        spec_box = Tk.ComboBox(self.entry_frame, label='Spectra', editable=False, dropdown=True,
                               command=self.choose_spec, value=self.choices_ts[1])
        spec_box.insert('end', self.choices_ts[0])
        spec_box.insert('end', self.choices_ts[1])
        spec_box.insert('end', self.choices_ts[2])
        spec_box.label.config(font=10)
        spec_box.entry.config(font=10)
        #spec_box.listbox.config(font=10)
        spec_box.pack(side='left', padx=10)

        # setting up combo box for timeseries
        hist_box = Tk.ComboBox(self.entry_frame, label='Timeseries', editable=False, dropdown=True,
                               command=self.choose_ts, value=self.choices_ts[0])
        hist_box.insert('end', self.choices_ts[0])
        hist_box.insert('end', self.choices_ts[1])
        hist_box.insert('end', self.choices_ts[2])
        hist_box.label.config(font=10)
        hist_box.entry.config(font=10)
        hist_box.pack(side='left', padx=10)

        # setting up earthquake info frame
        self.evtime = Tk.Label(self.eq_frame,
                          text='Event time: %s' % self.v2.stream[0].stats.smdict.eventtime.strftime("%d/%m/%Y %H:%M:%S"),
                          font=10, padx=20)
        self.evtime.pack(side='left')
        self.eqdist = Tk.Label(self.eq_frame, text='Epicentral distance: %d km' % self.v2.stream[0].stats.smdict.epicdist,
                          font=10, padx=20)
        self.eqdist.pack(side='left')
        self.hdep = Tk.Label(self.eq_frame, text='Hypocentral depth: %d km' % self.v2.stream[0].stats.smdict.hypodep,
                        font=10, padx=20)
        self.hdep.pack(side='left')
        self.lmag = Tk.Label(self.eq_frame, text='Local magnitude: %.2f' % self.v2.stream[0].stats.smdict.Ml,
                        font=10, padx=20)
        self.lmag.pack(side='left')
        a = self.data[0].split()
        fname = a[0].split('_')
        if len(fname) > 3:
            # building site
            self.sensname = fname[2]+"/"+fname[3]
        else:
            # single instrument accelerometer
            self.sensname = fname[2]
            
        self.sens = Tk.Label(self.eq_frame, text='Sensor name: %s' % self.sensname,
                        font=10, padx=20)
        self.sens.pack(side='left')


        # setting up navigation and save button
        p_button = Tk.Button(self.nav_frame, text='Previous', width=8, command=self.prev, font=10)
        p_button.pack(side='top', fill='x', anchor='center')
        n_button = Tk.Button(self.nav_frame, text='Next', width=8, command=self.next, font=10)
        n_button.pack(side='top', fill='x', anchor='center')
        n_button = Tk.Button(self.nav_frame, text='Save', width=8, command=self.savefile, font=10)
        n_button.pack(side='top', fill='x', anchor='center')


        # setting up radio buttons
        detrend = Tk.Checkbutton(self.nav_frame, text='Detrend', command=self.recalc,
                                 variable=self.p['detrend'], indicatoron=0, width=4, font=10)
        detrend.pack(side='top', fill='x', anchor='center')
        baldetrend = Tk.Balloon(self.nav_frame)
        baldetrend.bind_widget(detrend, balloonmsg='Choose whether to subtract linear trend from Volume 1 acceleration timeseries.') 

        demean = Tk.Checkbutton(self.nav_frame, text='Demean', command=self.recalc,
                                 variable=self.p['demean'], indicatoron=0, width=4, font=10)
        demean.pack(side='top', fill='x', anchor='center')
        baldemean = Tk.Balloon(self.nav_frame)
        baldemean.bind_widget(demean, balloonmsg='Choose whether to subtract mean from Volume 1 acceleration timeseries.') 

        maxb = Tk.Checkbutton(self.nav_frame, text='Max', command=self.plotmax,
                              variable=self.p['pmax'], indicatoron=0, width=4, font=10)
        maxb.pack(side='top', fill='x', anchor='center')
        balmaxb = Tk.Balloon(self.nav_frame)
        balmaxb.bind_widget(maxb, balloonmsg='Plot maxima of timeseries.') 

        fltrng = Tk.Checkbutton(self.nav_frame, text='Fltrng', command=self.plotfltrng,
                                variable=self.p['fltrng'], indicatoron=0, width=4, font=10)
        fltrng.pack(side='top', fill='x', anchor='center')
        balfltrng = Tk.Balloon(self.nav_frame)
        balfltrng.bind_widget(fltrng, balloonmsg='Plot cutoff and corner frequencies of highpass filter.') 

        cutrng = Tk.Checkbutton(self.nav_frame, text='Cutrng', command=self.plotmax,
                                variable=self.p['cutrng'], indicatoron=0, width=4, font=10)
        cutrng.pack(side='top', fill='x', anchor='center')
        balcutrng = Tk.Balloon(self.nav_frame)
        balcutrng.bind_widget(cutrng, balloonmsg='Plot cutting window.') 

        pltlog2 = Tk.Checkbutton(self.nav_frame, text='log2', command=self.plotfltrng,
                                 variable=self.p['pltlog2'], indicatoron=0, width=4, font=10)
        pltlog2.pack(side='top', fill='x', anchor='center')
        balpltlog2 = Tk.Balloon(self.nav_frame)
        balpltlog2.bind_widget(pltlog2, balloonmsg='Plot line with slope 2.0 through the maximum of the power spectrum.') 

        pltgrid = Tk.Checkbutton(self.nav_frame, text='Grid', command=self.plotfltrng,
                                 variable=self.p['pltgrid'], indicatoron=0, width=4, font=10)
        pltgrid.pack(side='top', fill='x', anchor='center')
        balpltgrid = Tk.Balloon(self.nav_frame)
        balpltgrid.bind_widget(pltgrid, balloonmsg='Plot grid lines.') 
        
        # setting up comment button
        self.p['comment'] = Tk.StringVar()
        cmnt_button = Tk.Button(self.nav_frame, text='Comment', width=8, command=self.add_comment, font=10)
        cmnt_button.pack(side='top', fill='x', anchor='center')
        cmnt_ent = Tk.Entry(self.nav_frame, textvariable=self.p['comment'], width=8)
        cmnt_ent.pack(side='top', fill='x', anchor='center')
        balcmnt = Tk.Balloon(self.nav_frame)
        balcmnt.bind_widget(cmnt_button, balloonmsg='Add a comment to the corresponding line in the input file.') 
        
    def add_comment(self):
        line = self.data[self.counter] 
        # delete potential old comment
        line = line[0:self.linel[self.counter]]
        # add comment
        self.data[self.counter] = line.rstrip() + "\t%s\n" % self.p['comment'].get() 
        
    def plotmax(self):
        """
        Function called by 'Max' radio button.
        """
        self.f2.clf()
        self.plottimeseries()
        self.canvas2.draw()
        
    def plotfltrng(self):
        """
        Function called by 'Flt' radio button.
        """
        self.f1.clf()
        self.plotspectra()
        self.canvas1.draw()
        
    def choose_ts(self, value):
        """
        Choose timeseries to display; called by combo box 'hist_box'.
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
        try:
            self.run_fortran()
        except FortranHandlerError, e:
            print e
            self.v1 = Vol12Reader(dummy=True)
            self.v2 = Vol12Reader(dummy=True)
            self.highp = [0., 0.]
            self.lowp = [0., 0.]
            self.npts = self.v1.stream[0].stats.npts
            self.dmn = 0
            self.dtrnd = 0
            self.startt = 0
            self.endt = 0
        except Vol12Error, e:
            print e
            self.v1 = Vol12Reader(dummy=True)
            self.v2 = Vol12Reader(dummy=True)
            self.highp = [0., 0.]
            self.lowp = [0., 0.]
            self.npts = self.v1.stream[0].stats.npts
            self.dmn = 0
            self.dtrnd = 0
            self.startt = 0
            self.endt = 0

        self.plotspectra()
        self.plottimeseries()
        
    def plotspectra(self, xrange=(0.01, 20.), yrngfact=0.2):
        """
        Plot the spectra using Matplotlib.
        """
        try:
            fspec1, fspec2, fspec3, freqs = self.getspectra(self.choices_ts, self.spec_old)
            idx = np.where((freqs >= xrange[0]) & (freqs <= xrange[1]))
            # get maxima within the plotting range of interest
            max1 = abs(fspec1[idx]).max()
            min1 = abs(fspec1[idx]).min()
            ymin1 = min1 - yrngfact * min1
            ymax1 = max1 + yrngfact * max1
            max2 = abs(fspec2[idx]).max()
            min2 = abs(fspec2[idx]).min()
            ymin2 = min2 - yrngfact * min2
            ymax2 = max2 + yrngfact * max2
            max3 = abs(fspec3[idx]).max()
            min3 = abs(fspec3[idx]).min()
            ymin3 = min3 - yrngfact * min3
            ymax3 = max3 + yrngfact * max3
    
            ax1 = self.f1.add_subplot(3, 1, 1)
            ax2 = self.f1.add_subplot(3, 1, 2, sharex=ax1)
            ax3 = self.f1.add_subplot(3, 1, 3, sharex=ax1)
            ax1.loglog(freqs, abs(fspec1))
            ax2.loglog(freqs, abs(fspec2))
            ax3.loglog(freqs, abs(fspec3))
            
            if self.p['fltrng'].get():
                # plot high pass filter range
                ax1.vlines(self.highp[0], ymin1, ymax1)
                ax1.vlines(self.highp[1], ymin1, ymax1)
                ax2.vlines(self.highp[0], ymin2, ymax2)
                ax2.vlines(self.highp[1], ymin2, ymax2)
                ax3.vlines(self.highp[0], ymin3, ymax3)
                ax3.vlines(self.highp[1], ymin3, ymax3)
                
            if self.p['pltlog2'].get() == 1:
                # plot a line with slope 2.0 through the point in the accelerogram
                # that corresponds to the maximum displacement
                fdisp1, fdisp2, fdisp3, frdisp = self.getspectra(self.choices_ts, self.choices_ts[0])
                facc1, facc2, facc3, fracc = self.getspectra(self.choices_ts, self.spec_old)
                idx1 = np.where((frdisp >= xrange[0]) & (frdisp <= xrange[1]))
                ifmax1 = abs(fdisp1[idx1]).argmax()
                fmax1 = (frdisp[idx1])[ifmax1]
                ind1 = int(abs(fracc - fmax1).argmin())
                saccmax1 = abs(facc1[ind1])
                try:
                    ax1.plot(fmax1, saccmax1, 'ro')
                    ax1.plot([fmax1, xrange[1]], [saccmax1, saccmax1 * 10 ** (2. * m.log10(xrange[1] / fmax1))], 'k--')
                    ax1.plot([fmax1, xrange[0]], [saccmax1, saccmax1 * 10 ** (-2. * m.log10(fmax1 / xrange[0]))], 'k--')
                except Exception, e:
                    print e
                    print fmax1, saccmax1
                ifmax2 = abs(fdisp2[idx1]).argmax()
                fmax2 = (frdisp[idx1])[ifmax2]
                ind2 = int(abs(fracc - fmax2).argmin())
                saccmax2 = abs(facc2[ind2])
                #saccmax2 = abs(facc2[idx1])[ifmax2]
                try: 
                    ax2.plot(fmax2, saccmax2, 'ro')
                    ax2.plot([fmax2, xrange[1]], [saccmax2, saccmax2 * 10 ** (2. * m.log10(xrange[1] / fmax2))], 'k--')
                    ax2.plot([fmax2, xrange[0]], [saccmax2, saccmax2 * 10 ** (-2. * m.log10(fmax2 / xrange[0]))], 'k--')
                except Exception, e:
                    print e
                    print fmax2, saccmax2
                ifmax3 = abs(fdisp3[idx1]).argmax()
                fmax3 = (frdisp[idx1])[ifmax3]
                ind3 = int(abs(fracc - fmax3).argmin())
                saccmax3 = abs(facc3[ind3])
                #saccmax3 = abs(facc3[idx1])[ifmax3]
                try:
                    ax3.plot(fmax3, saccmax3, 'ro')
                    ax3.plot([fmax3, xrange[1]], [saccmax3, saccmax3 * 10 ** (2. * m.log10(xrange[1] / fmax3))], 'k--')
                    ax3.plot([fmax3, xrange[0]], [saccmax3, saccmax3 * 10 ** (-2. * m.log10(fmax3 / xrange[0]))], 'k--')
                except Exception, e:
                    print e
                    print fmax3, saccmax3
            else:
                 self.p['pltlog2'].set(0)
    
            if self.p['pltgrid'].get():
                ax1.grid()
                ax2.grid()
                ax3.grid()
                
            ax1.set_xlim(xrange)
            ax2.set_xlim(xrange)
            ax3.set_xlim(xrange)
            ax1.set_ylim(ymin1, ymax1)
            ax2.set_ylim(ymin2, ymax2)
            ax3.set_ylim(ymin3, ymax3)
            ax1.set_xticklabels(ax1.get_xticks(), visible=False)
            ax2.set_xticklabels(ax2.get_xticks(), visible=False)
            ax3.set_xlabel('Frequency [Hz]')
            ax1.set_title(self.v2.stream[0].stats.station)
        except Exception, e:
            print "Problems in plotting the spectra of %s" % (self.data[self.counter].split()[0])
            print "Please check the Volume 1 and Volume 2 file for possible problems."
            print "Error: %s" % (e) 
    
    def plottimeseries(self, noticks=6):
        """
        Plot the timeseries using Matplotlib.
        """
        try:
            tr1, tr2, tr3, time = self.gettimeseries(self.choices_ts, self.hist_old)
            append = tr1.stats.smdict.append
            prepend = tr1.stats.smdict.prepend
            npts = tr1.stats.npts
            delta = tr1.stats.delta
            npts -= prepend
            # find indices of prepended and appended samples to color them 
            # differently
            time = np.r_[np.arange(-prepend, 0, 1), np.arange(npts)] * delta
            xmax = time.max()
            xmin = time.min()
            idxlower = np.where(time < 0.)
            idxupper = np.where(time > (npts - append) * delta)
            axislist = []
            tracelist = [tr1, tr2, tr3]
            if xmin < 0.:
                ticklist = np.r_[xmin, np.arange(10, xmax, 10.)]
                stind = 1
            else:
                ticklist = np.arange(10, xmax, 10.)
                stind = 0
            labellist = [str(i) for i in ticklist]
            labelmajor = tr1.stats.starttime.strftime('%H:%M:%S')
            for i in xrange(3):
                if i > 0:
                    ax = self.f2.add_subplot(3, 1, i + 1, sharex=axislist[0])
                else:
                    ax = self.f2.add_subplot(3, 1, i + 1)
                axislist.append(ax)
                tr = tracelist[i]
                ax.plot(time, tr.data, label=tr.stats.channel)
                ax.plot(time[idxlower], tr.data[idxlower], 'r')
                ax.plot(time[idxupper], tr.data[idxupper], 'r')
                ax.set_xticks(ticklist, minor=True)
                ax.set_xticks([0], minor=False)
                ax.legend(loc='upper right')
                ymax = abs(tr.data).max()
                ymax += 0.1 * ymax

                if self.p['pmax'].get():
                    idmax = abs(tr.data).argmax()
                    max = tr.data[idmax]
                    ax.plot(time[idmax], max, 'ro')
                if self.p['cutrng'].get():
                    if self.hist_old == self.choices_ts[2]:
                        if int(self.startt / delta) < int(self.endt / delta):
                            if int(self.startt / delta) < tr.stats.npts and int(self.endt / delta) < tr.stats.npts:
                                t1 = self.startt
                                t2 = self.endt
                                ax.vlines(t1, -ymax, ymax, color='k')
                                ax.vlines(t2, -ymax, ymax, color='k')
                if i < 2:
                    ax.set_xticklabels(labellist, visible=False, minor=True)
                    ax.set_xticklabels([labelmajor], visible=False, minor=False)
                else:
                    ax.set_xticklabels(labellist, visible=True, minor=True)
                    ax.set_xticklabels([labelmajor], visible=True, minor=False)
                    ax.tick_params(direction='out', axis='x', length=10, pad=10, top='off')
                    ax.set_xlabel('Time [s]')
                ax.set_ylim(-ymax, ymax)
                ax.set_xlim(xmin, xmax)
            axislist[0].set_title(tr1.stats.station)

        except Exception, e:
            print "Problems in plotting the timeseries of %s" % (self.data[self.counter].split()[0])
            print "Please check the Volume 1 and Volume 2 file for possible problems."
            print "Error: %s" % (e) 

    def update(self):
        """
        This function is called when the filter parameter or the length of the 
        time series changes.
        """
        self.f1.clf();self.f2.clf()
        self.specs = {0:None, 1:None, 2:None}
        self.plotcanvas()
        self.canvas1.draw()
        self.canvas2.draw()
        self.p['hlow'].set(self.highp[0])
        self.p['hhgh'].set(self.highp[1])
        self.p['starttrim'].set(self.startt)
        self.p['endtrim'].set(self.endt)
        self.p['demean'].set(self.dmn)
        self.p['detrend'].set(self.dtrnd)
        line = self.data[self.counter]
        if line[self.linel[self.counter] - 1] == '\n':
            self.p['comment'].set('')
        else:
            oldcmnt = line[(self.linel[self.counter] - 1):-1]
            self.p['comment'].set(oldcmnt.strip())
        self.eqdist.config(text='Epicentral distance: %d km' % self.v2.stream[0].stats.smdict.epicdist)
        self.evtime.config(text='Event time: %s' % self.v2.stream[0].stats.smdict.eventtime.strftime("%d/%m/%Y %H:%M:%S"))
        self.hdep.config(text='Hypocentral depth: %d km' % self.v2.stream[0].stats.smdict.hypodep)
        self.lmag.config(text='Local magnitude: %.2f' % self.v2.stream[0].stats.smdict.Ml)
        a = line.split()
        fname = a[0].split('_')
        if len(fname) > 3:
            # building site
            self.sensname = fname[2]+"/"+fname[3]
        else:
            # single instrument accelerometer
            self.sensname = fname[2]
        self.sens.config(text='Sensor name: %s' % self.sensname)

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
        #nline = "%-20s%6.2f%6.2f" % (a[0], self.p['hlow'].get(), self.p['hhgh'].get())
        nline = "%s%6.2f%6.2f" % (a[0], self.p['hlow'].get(), self.p['hhgh'].get())
        #nline += line[32:72]
        nline += "%6.2f%6.2f%6d%10d %06d"%(float(a[3]),float(a[4]),int(a[5]),int(a[6]),int(a[7]))
        nline += "%5.2f"%(float(a[8]))
        nline += "%6d%6d" % (self.p['starttrim'].get(),self.p['endtrim'].get())
        nline += "%2d%2d" % (self.p['demean'].get(),self.p['detrend'].get())
        nline += line[self.linel[self.counter] - 1::]
        print "old line: ", line
        print "new line: ", nline
        try:
            self.check_filterband()
        except FilterError, e:
            print e
        else:
            self.data[self.counter] = nline
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
