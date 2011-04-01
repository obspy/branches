#!/usr/bin/env python
#
# PyQt API:
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html
# Tutorials:
# http://zetcode.com/tutorials/pyqt4/

import os
import sys
import optparse

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QEvent, Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

from obspy.signal import pazToFreqResp

class MyMainWindow(QtGui.QMainWindow):
    """
    Main Window docstring...
    """
    def __init__(self, options):
        # make all commandline options available for later use
        # e.g. in update() methods
        self.options = options
        # for convenience set some instance wide attributes
        self.poles = options.poles
        self.zeros = options.zeros
        self.file = options.file

        # put some addtional setup stuff here...
        tmp = np.loadtxt(self.file).T
        self.freq = tmp[0]
        self.ampl = tmp[1]
        self.phase = tmp[2]

        # setup initial poles/zeros
        self.paz = {}
        self.paz['poles'] = [0.06+0j, 206+0j]
        self.paz['zeros'] = [0+0j, 0+0j]
        self.paz['gain'] = 206
        
        # setup GUI
        QtGui.QMainWindow.__init__(self)
        self.__setup_GUI()
        self.__connect_signals()

        # make initial plot and show it
        self.update()
        self.canv.show()
        self.show()

    def __setup_GUI(self):
        """
        Add matplotlib canvas, some buttons and stuff...
        """
        self.setWindowTitle("FitResp")
        self.setGeometry(300, 300, 500, 500)
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
        self.buttons_real = []
        self.buttons_imag = []
        for i, pole in enumerate(self.paz['poles']):
            button_real = QtGui.QDoubleSpinBox()
            button_real.setMaximum(1e3)
            button_real.setMinimum(-1e3)
            button_real.setSingleStep(1)
            button_real.setValue(pole.real)
            hlayout.addWidget(QtGui.QLabel("pole %i real" % (i + 1)))
            hlayout.addWidget(button_real)
            button_imag = QtGui.QDoubleSpinBox()
            button_imag.setMaximum(1e3)
            button_imag.setMinimum(-1e3)
            button_imag.setSingleStep(1)
            button_imag.setValue(pole.imag)
            hlayout.addWidget(QtGui.QLabel("imag"))
            hlayout.addWidget(button_imag)
            self.buttons_real.append(button_real)
            self.buttons_imag.append(button_imag)

        #
        #self.qDoubleSpinBox_high = QtGui.QDoubleSpinBox()
        #self.qDoubleSpinBox_high.setValue(self.options.high)
        #hlayout.addWidget(QtGui.QLabel("high"))
        #hlayout.addWidget(self.qDoubleSpinBox_high)

        #self.qCheckBox_zerophase = QtGui.QCheckBox()
        #self.qCheckBox_zerophase.setChecked(self.options.zerophase)
        #self.qCheckBox_zerophase.setText("zerophase")
        #hlayout.addWidget(self.qCheckBox_zerophase)

        qToolBar = QtGui.QToolBar()
        self.toolbar = NavigationToolbar2QTAgg(canv, qToolBar)
        qToolBar.addWidget(self.toolbar)
        qToolBar.setMovable(False)
        qToolBar.setFloatable(False)
        self.addToolBar(Qt.BottomToolBarArea, qToolBar)

        # make matplotlib stuff available
        self.canv = canv
        self.fig = canv.figure
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

    def __connect_signals(self):
        """
        Connect button signals to methods...
        """
        connect = QtCore.QObject.connect
        for button in self.buttons_real + self.buttons_imag:
            connect(button,
                    QtCore.SIGNAL("valueChanged(double)"),
                    self.on_anyButton_valueChanged)
        #connect(self.qDoubleSpinBox_high,
        #        QtCore.SIGNAL("valueChanged(double)"),
        #        self.on_qDoubleSpinBox_high_valueChanged)
        #connect(self.qCheckBox_zerophase,
        #        QtCore.SIGNAL("stateChanged(int)"),
        #        self.on_qCheckBox_zerophase_stateChanged)

    def update(self):
        """
        This method should do everything to update the plot.
        """
        # clear axes before anything else
        ax1 = self.ax1
        ax1.clear()
        ax2 = self.ax2
        ax2.clear()

        ax1.loglog(self.freq, self.ampl)
        ax2.semilogx(self.freq, self.phase)

        # plot theoretical responses from paz here
        paz = self.paz
        h, f = pazToFreqResp(paz['poles'], paz['zeros'], paz['gain'], 0.005,
                             16384, freq=True)
        ampl = abs(h)
        phase = np.unwrap(np.arctan2(-h.imag, h.real)) #take negative of imaginary part
        ax1.loglog(f, ampl, color="r")
        ax2.semilogx(f, phase, color="r")

        # update matplotlib canvas
        self.canv.draw()
    
    def on_anyButton_valueChanged(self, newvalue):
        for i, button in enumerate(self.buttons_real):
            real = button.value()
            imag = self.paz['poles'][i].imag
            self.paz['poles'][i] = complex(real, imag)
        for i, button in enumerate(self.buttons_imag):
            real = self.paz['poles'][i].real
            imag = button.value()
            self.paz['poles'][i] = complex(real, imag)
        self.update()

    #def on_qDoubleSpinBox_high_valueChanged(self, newvalue):
    #    self.high = newvalue
    #    self.update()

    #def on_qCheckBox_zerophase_stateChanged(self, value):
    #    self.zerophase = self.qCheckBox_zerophase.isChecked()
    #    self.update()


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


def main():
    """
    Gets executed when the program starts.
    """
    usage = "Usage information goes here..."
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--poles", type=int, dest="poles", default=3,
                      help="Number of Poles")
    parser.add_option("-z", "--zeros", type=int, dest="zeros", default=2,
                      help="Number of Zeros")
    parser.add_option("-f", "--file", type=str, dest="file", default="res_unknown",
                      help="Filename of relcalstack output")
    (options, args) = parser.parse_args()

    qApp = QtGui.QApplication(sys.argv)
    myMainWindow = MyMainWindow(options)
    os._exit(qApp.exec_())


if __name__ == "__main__":
    main()
