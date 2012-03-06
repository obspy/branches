#!/usr/bin/env python
#
# PyQt API:
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html
# Tutorials:
# http://zetcode.com/tutorials/pyqt4/

import os
import sys
import optparse
import fnmatch

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QEvent, Qt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.transforms
from scipy.integrate import cumtrapz
from scipy.signal import detrend
import scipy as sp
from matplotlib.patches import Ellipse
from matplotlib.ticker import FuncFormatter, FormatStrFormatter, MaxNLocator
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as QNavigationToolbar
from matplotlib.backend_bases import MouseEvent as MplMouseEvent, KeyEvent as MplKeyEvent

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

from obspy.core import read, UTCDateTime, Stream
from obspy.seishub import Client
from obspy.signal.trigger import triggerOnset, recStaltaPy




class MyMainWindow(QtGui.QMainWindow):
    """
    Main Window docstring...
    """
    def __init__(self, options):
        # make all commandline options available for later use
        # e.g. in update() methods
        self.options = options
        # for convenience set some instance wide attributes
        self.low = options.low
        self.high = options.high
        self.zerophase = options.zerophase
        self.server = options.server
        self.duration = options.duration
        self.time = UTCDateTime(options.start)
        self.T0 = UTCDateTime(options.start)
        self.redraw = 0
        self.integrate = options.integrate
        self.trigger = options.trigger
        self.lta = options.lta
        self.sta = options.sta
        self.thres1 = options.thres1
        self.thres2 = options.thres2

        # setup GUI
        QtGui.QMainWindow.__init__(self)
        self.__setup_GUI()
        self.__connect_signals()

        # put some addtional setup stuff here...
        # connect to the server and go through channel list
        sta_fetched = set()
        self.streams = []
        self.client = Client(base_url=self.server,user='admin',password='admin',timeout=10)
        self.d = self.time + self.duration
        self.ids = options.seishub_ids
        for id in options.seishub_ids.split(","):
            net, sta_wildcard, loc, cha = id.split(".")
            stations_to_fetch = []
            if "?" in sta_wildcard or "*" in sta_wildcard:
                for sta in sorted(self.client.waveform.getStationIds(network=net)):
                    if fnmatch.fnmatch(sta, sta_wildcard):
                        stations_to_fetch.append(sta)
            else:
                stations_to_fetch = [sta_wildcard]
            for sta in stations_to_fetch:
                # make sure we dont fetch a single station of
                # one network twice (could happen with wildcards)
                net_sta = "%s.%s.%s" % (net, sta, cha)
                if net_sta in sta_fetched:
                    print "%s skipped! (Was already retrieved)" % net_sta.ljust(8)
                    continue
                try:
                    sys.stdout.write("\r%s ..." % net_sta.ljust(8))
                    sys.stdout.flush()
                    st = self.client.waveform.getWaveform(net, sta, loc, cha, self.time,
                            self.d, apply_filter=False, getPAZ=True)
                            
                    sta_fetched.add(net_sta)
                    sys.stdout.write("\r%s fetched.\n" % net_sta.ljust(8))
                    sys.stdout.flush()
                except Exception, e:
                    sys.stdout.write("\r%s skipped! (Server replied: %s)\n" % (net_sta.ljust(8), e))
                    sys.stdout.flush()
                    continue
                for tr in st:
                    tr.stats['_format'] = "SeisHub"
                self.streams.append(st)

        
        # make initial plot and show it
        self.update()
        self.canv.show()
        self.show()

    def __setup_GUI(self):
        """
        Add matplotlib canvas, some buttons and stuff...
        """
        self.setWindowTitle("Quicklook")
        self.setGeometry(300, 300, 1000, 500)
        main = QtGui.QWidget()
        self.setCentralWidget(main)
        # add matplotlib canvas and setup layouts to put buttons in
        vlayout = QtGui.QVBoxLayout()
        vlayout.addStretch(1)
        main.setLayout(vlayout)
        canv = QMplCanvas()
        vlayout.addWidget(canv)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch(1)
        vlayout.addLayout(hlayout)

        # add some buttons
        self.qCheckBox_trigger = QtGui.QCheckBox()
        self.qCheckBox_trigger.setChecked(self.options.trigger)
        self.qCheckBox_trigger.setText("trigger")
        hlayout.addWidget(self.qCheckBox_trigger)

        self.qDoubleSpinBox_sta = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_sta.setValue(self.options.sta)
        hlayout.addWidget(QtGui.QLabel("sta"))
        hlayout.addWidget(self.qDoubleSpinBox_sta)
        
        self.qDoubleSpinBox_lta = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_lta.setValue(self.options.lta)
        hlayout.addWidget(QtGui.QLabel("lta"))
        hlayout.addWidget(self.qDoubleSpinBox_lta)
        
        self.qDoubleSpinBox_thres1 = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_thres1.setValue(self.options.thres1)
        hlayout.addWidget(QtGui.QLabel("up"))
        hlayout.addWidget(self.qDoubleSpinBox_thres1)
        
        self.qDoubleSpinBox_thres2 = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_thres2.setValue(self.options.thres2)
        hlayout.addWidget(QtGui.QLabel("down"))
        hlayout.addWidget(self.qDoubleSpinBox_thres2)
        
        self.qCheckBox_integrate = QtGui.QCheckBox()
        self.qCheckBox_integrate.setChecked(self.options.integrate)
        self.qCheckBox_integrate.setText("integrate")
        hlayout.addWidget(self.qCheckBox_integrate)
 
        self.qDoubleSpinBox_low = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_low.setValue(self.options.low)
        hlayout.addWidget(QtGui.QLabel("low"))
        hlayout.addWidget(self.qDoubleSpinBox_low)
        
        self.qDoubleSpinBox_high = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_high.setValue(self.options.high)
        hlayout.addWidget(QtGui.QLabel("high"))
        hlayout.addWidget(self.qDoubleSpinBox_high)

        self.qCheckBox_zerophase = QtGui.QCheckBox()
        self.qCheckBox_zerophase.setChecked(self.options.zerophase)
        self.qCheckBox_zerophase.setText("zerophase")
        hlayout.addWidget(self.qCheckBox_zerophase)

        self.qPush_Button_goback = QtGui.QPushButton()
        self.qPush_Button_goback.setObjectName("Previous")
        self.qPush_Button_goback.setText("Previous")
        hlayout.addWidget(self.qPush_Button_goback)

        self.qPush_Button_goahead = QtGui.QPushButton()
        self.qPush_Button_goahead.setObjectName("Next")
        self.qPush_Button_goahead.setText("Next")
        hlayout.addWidget(self.qPush_Button_goahead)

        qToolBar = QtGui.QToolBar()
        self.toolbar = NavigationToolbar2QTAgg(canv, qToolBar)
        qToolBar.addWidget(self.toolbar)
        qToolBar.setMovable(False)
        qToolBar.setFloatable(False)
        self.addToolBar(Qt.BottomToolBarArea, qToolBar)

        # make matplotlib stuff available
        self.canv = canv
        self.fig = canv.figure
        self.ax = self.fig.add_subplot(111)

    def __connect_signals(self):
        """
        Connect button signals to methods...
        """
        connect = QtCore.QObject.connect
        connect(self.qCheckBox_integrate,
                QtCore.SIGNAL("stateChanged(int)"),
                self.on_qCheckBox_integrate_stateChanged)
        connect(self.qDoubleSpinBox_low,
                QtCore.SIGNAL("valueChanged(double)"),
                self.on_qDoubleSpinBox_low_valueChanged)
        connect(self.qDoubleSpinBox_high,
                QtCore.SIGNAL("valueChanged(double)"),
                self.on_qDoubleSpinBox_high_valueChanged)
        connect(self.qCheckBox_zerophase,
                QtCore.SIGNAL("stateChanged(int)"),
                self.on_qCheckBox_zerophase_stateChanged)
        connect(self.qCheckBox_trigger,
                QtCore.SIGNAL("stateChanged(int)"),
                self.on_qCheckBox_trigger_stateChanged)
        connect(self.qPush_Button_goahead,
                QtCore.SIGNAL("clicked(bool)"),
                self.on_qPush_Button_goahead_stateChanged)
        connect(self.qPush_Button_goback,
                QtCore.SIGNAL("clicked(bool)"),
                self.on_qPush_Button_goback_stateChanged)

    def getData(self):
        sta_fetched = set()
        self.streams = []
        for id in self.ids.split(","):
            net, sta_wildcard, loc, cha = id.split(".")
            stations_to_fetch = []
            if "?" in sta_wildcard or "*" in sta_wildcard:
                for sta in sorted(self.client.waveform.getStationIds(network=net)):
                    if fnmatch.fnmatch(sta, sta_wildcard):
                        stations_to_fetch.append(sta)
            else:
                stations_to_fetch = [sta_wildcard]
            for sta in stations_to_fetch:
                # make sure we dont fetch a single station of
                # one network twice (could happen with wildcards)
                net_sta = "%s.%s.%s" % (net, sta, cha)
                if net_sta in sta_fetched:
                    print "%s skipped! (Was already retrieved)" % net_sta.ljust(8)
                    continue
                try:
                    sys.stdout.write("\r%s ..." % net_sta.ljust(8))
                    sys.stdout.flush()
                    st = self.client.waveform.getWaveform(net, sta, loc, cha, self.t,
                            self.d, apply_filter=False, getPAZ=True)

                    sta_fetched.add(net_sta)
                    sys.stdout.write("\r%s fetched.\n" % net_sta.ljust(8))
                    sys.stdout.flush()
                except Exception, e:
                    sys.stdout.write("\r%s skipped! (Server replied: %s)\n" % (net_sta.ljust(8), e))
                    sys.stdout.flush()
                    continue
                for tr in st:
                    tr.stats['_format'] = "SeisHub"
                self.streams.append(st)

    def time_abs2rel(self, abstime):
        """
        Converts an absolute UTCDateTime to the time in ObsPyck's relative time
        frame.

        :type abstime: :class:`obspy.core.utcdatetime.UTCDateTime`
        :param abstime: Absolute time in UTC.
        :returns: time in ObsPyck's relative time as a float
        """
        return abstime - self.T0


    def update(self):
        stNum = len(self.streams)
        fig = self.fig
        axs = []
        self.axs = axs
        plts = []
        self.plts = plts
        trans = []
        self.trans = trans
        t = []
        fx = open("trigger",'a')
        for i, st in enumerate(self.streams):
            # if (tr = st.select(component="Z")[0]):
            tr = st[0]
            # make sure that the relative x-axis times start with 0 at the time
            # specified as start time on command line
            starttime_relative = self.time_abs2rel(tr.stats.starttime)
            sampletimes = np.arange(starttime_relative,
                    starttime_relative + (tr.stats.delta * tr.stats.npts),
                    tr.stats.delta)
            # sometimes our arange is one item too long (why??), so we just cut
            # off the last item if this is the case
            if len(sampletimes) == tr.stats.npts + 1:
                sampletimes = sampletimes[:-1]
            t.append(sampletimes)
            if i == 0:
               if self.redraw == 1:
                  if ax.lines:
                      xlims = list(ax.get_xlim())
                      ylims = list(ax.get_ylim())
                  ax.clear()
               ax = fig.add_subplot(stNum, 1, i+1)
            else:
                ax = fig.add_subplot(stNum, 1, i+1, sharex=axs[0], sharey=axs[0])
                ax.xaxis.set_ticks_position("top")
            axs.append(ax)
            trans.append(matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes))
            ax.xaxis.set_major_formatter(FuncFormatter(formatXTicklabels))
            tr = tr.copy()
            detrend(tr.data)
            tr.data -= tr.data.mean()
            tr.filter("highpass", {'freq': self.low,
                               'zerophase': self.zerophase})
            tr.filter("lowpass", {'freq': self.high,
                               'zerophase': self.zerophase})
            if self.integrate:
                tr.data = cumtrapz(tr.data,dx=tr.stats.delta)
                sampletimes = sampletimes[:-1]
                #import pdb; pdb.set_trace()
                poly = sp.polyfit(sampletimes,tr.data,2);
                dem = sp.polyval([poly[0],poly[1],poly[2]],sampletimes)
		tr.data -= dem
            
            df = 1./tr.stats.delta

            if self.trigger:
                cft = recStaltaPy(tr.data,self.sta*df,self.lta*df)
                on_of = triggerOnset(cft,self.thres1,self.thres2)
                on_of = starttime_relative + (tr.stats.delta * on_of)
                fx.write("%s %s %s"%(tr.stats.station,on_of[:,0],on_of[:,1]))

            # normalize with overall sensitivity and convert to nm/s
            # if not explicitly deactivated on command line
            if not self.options.nonormalization:
                # special handling for GSE2 data: apply calibration
                calib = 1.0
                if tr.stats._format == "GSE2":
                    calib = tr.stats.calib * 2 * np.pi / tr.stats.gse2.calper
                if self.trigger:
                   plt.ion()
                   xx = ax.plot(sampletimes, tr.data * 1e9 / tr.stats.paz.sensitivity / calib, color='k', zorder=1000)[0]
                   ymin, ymax = ax.get_ylim()
                   ax.vlines(on_of[:,0],ymin, ymax, color='r',linewidth=2)
                   ax.vlines(on_of[:,1],ymin, ymax, color='b',linewidth=2)
                   plts.append(ax)
                else:
                   xx = ax.plot(sampletimes, tr.data * 1e9 / tr.stats.paz.sensitivity / calib, color='k', zorder=1000)[0]
                   plts.append(ax)

            else:
                if self.trigger:
                   xx = ax.plot(sampletimes, tr.data, color='k', zorder=1000)[0]
                   ymin, ymax = ax.get_ylim()
                   ax.vlines(on_of[:,0],ymin, ymax, color='r',linewidth=2)
                   ax.vlines(on_of[:,1],ymin, ymax, color='b',linewidth=2)
                   plts.append(ax)
                else:
                   xx = ax.plot(sampletimes, tr.data, color='k', zorder=1000)[0]
                   plts.append(ax)

        fx.close()
        self.drawIds()
#        axs[-1].xaxis.set_ticks_position("both")

        label = self.T0.isoformat().replace("T", "  ")
        self.supTit = fig.suptitle(label, ha="left", va="bottom",
                                   x=0.01, y=0.01)
#        self.xMin, self.xMax = axs[0].get_xlim()
#        self.yMin, self.yMax = axs[0].get_ylim()
        fig.subplots_adjust(bottom=0.001, hspace=0.000, right=0.999, top=0.999, left=0.001)

    def drawIds(self):
        """
        draws the trace ids plotted as text into each axes.
        """
        # make a Stream with the traces that are plotted
        # tmp_stream = Stream([st[0] for st in self.streams])
        tmp_stream = Stream([st[0] for st in self.streams])
        for ax, tr in zip(self.axs, tmp_stream):
            ax.text(0.01, 0.95, tr.id, va="top", ha="left", fontsize=18,
                    family='monospace', color="blue", zorder=10000,
                    transform=ax.transAxes)


#    def update(self):
#        """
#        This method should do everything to update the plot.
#        """
#        # clear axes before anything else
#        ax = self.ax
#        if ax.lines:
#            xlims = list(ax.get_xlim())
#            ylims = list(ax.get_ylim())
#        ax.clear()
#
#        st = self.st.copy()
#        st[0].data -= st[0].data.mean()
#        st.filter("bandpass", {'freqmin': self.low, 'freqmax': self.high,
#                               'zerophase': self.zerophase})
#        tr = st.select(component="Z")[0]
#        ax.plot(tr.data)
#        # update matplotlib canvas
#        try:
#            ax.set_xlim(xlims)
#            ax.set_ylim(ylims)
#        except UnboundLocalError:
#            pass
#        self.canv.draw()
    
    def on_qDoubleSpinBox_low_valueChanged(self, newvalue):
        self.low = newvalue
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()


    def on_qDoubleSpinBox_high_valueChanged(self, newvalue):
        self.high = newvalue
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()

    def on_qDoubleSpinBox_lta_valueChanged(self, newvalue):
        self.high = newvalue

    def on_qDoubleSpinBox_sta_valueChanged(self, newvalue):
        self.high = newvalue

    def on_qDoubleSpinBox_tr1_valueChanged(self, newvalue):
        self.thresh1 = newvalue

    def on_qDoubleSpinBox_tr2_valueChanged(self, newvalue):
        self.thresh2 = newvalue

    def on_qPush_Button_goahead_stateChanged(self,value):
        print self.time
        self.time = self.time + self.duration
        self.t = UTCDateTime(self.time)
        self.d = self.t + self.duration
	self.st = []
        self.st = self.getData()
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()


    def on_qPush_Button_goback_stateChanged(self,value):
        self.time = self.time - self.duration
        self.t = UTCDateTime(self.time)
        self.d = self.t + self.duration
	self.st = []
        self.st = self.getData()
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()


    def on_qCheckBox_zerophase_stateChanged(self, value):
        self.zerophase = self.qCheckBox_zerophase.isChecked()
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()

    def on_qCheckBox_trigger_stateChanged(self, value):
        self.trigger = self.qCheckBox_trigger.isChecked()
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()

    def on_qCheckBox_integrate_stateChanged(self, value):
        self.integrate = self.qCheckBox_integrate.isChecked()
        self.delAxes()
        self.fig.clear()
        self.update()
        self.canv.draw()

    def delAxes(self):
        for ax in self.axs:
            if ax in self.fig.axes:
                self.fig.delaxes(ax)
            del ax
        if self.supTit in self.fig.texts:
            self.fig.texts.remove(self.supTit)

    def redraw(self):
        for line in self.multicursor.lines:
            line.set_visible(False)
        self.canv.draw()





class QMplCanvas(FigureCanvasQTAgg):
    """
    Class to represent the FigureCanvas widget.
    """
    def __init__(self, parent=None):
        # Standard Matplotlib code to generate the plot
        self.fig = plt.Figure()
        # initialize the canvas where the Figure renders into
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

def formatXTicklabels(x, *pos):
    """
    Make a nice formatting for y axis ticklabels: minutes:seconds.microsec
    """
    # x is of type numpy.float64, the string representation of that float
    # strips of all tailing zeros
    # pos returns the position of x on the axis while zooming, None otherwise
    min = int(x / 60.)
    if min > 0:
        sec = x % 60
        return "%i:%06.3f" % (min, sec)
    else:
        return "%.3f" % x



def main():
    """
    Gets executed when the program starts.
    """
    usage = "Usage information goes here..."
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--low", type=float, dest="low", default=0.01,
                      help="Lowpass frequency")
    parser.add_option("--high", type=float, dest="high", default=10.0,
                      help="Highpass frequency")
    parser.add_option("-z", "--zerophase", action="store_true",
                      dest="zerophase", default=False,
                      help="Use zerophase filter option")
    parser.add_option("--server", dest="server", default="http://10.153.82.3:9080",
                      help="server to grap data from")
    parser.add_option("-i","--seishub_ids", dest="seishub_ids", help="list channels in SDS structure")
    parser.add_option("-s", "--start", dest="start", help="start time", default='2011-06-02T00:00:00')
    parser.add_option("-d", "--duration", dest="duration", type=float, default=60, help="duration in seconds")
    parser.add_option("--trigger", action="store_true",dest="trigger", default=False, help="trigger")
    parser.add_option("--sta", dest="sta", type=float, default=0.5, help="sta in seconds")
    parser.add_option("--lta", dest="lta", type=float, default=10.0, help="lta in seconds")
    parser.add_option("--thres1", dest="thres1", type=float, default=3.5, help="start trigger treshold")
    parser.add_option("--thres2", dest="thres2", type=float, default=0.5, help="end trigger treshold")
    parser.add_option("--integrate", action="store_true",dest="integrate", default=False, help="integration")
    parser.add_option("--nonormalization", 
                dest="nonormalization", default=False,
                help= "Deactivate normalization to nm/s for plotting " + \
                "using overall sensitivity (tr.stats.paz.sensitivity)")
    (options, args) = parser.parse_args()

    
    qApp = QtGui.QApplication(sys.argv)
    myMainWindow = MyMainWindow(options)
    os._exit(qApp.exec_())
   


if __name__ == "__main__":
    main()
