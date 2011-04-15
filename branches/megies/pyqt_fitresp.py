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
        self.file = options.file

        # put some addtional setup stuff here...
        tmp = np.loadtxt(self.file).T
        self.freq = tmp[0]
        self.ampl = tmp[1]
        self.phase = tmp[2]

        # setup initial poles/zeros
        self.paz = {}
        self.paz['poles'] = parse_paz_string(options.poles)
        self.paz['zeros'] = parse_paz_string(options.zeros)
        self.paz['gain'] = options.normalization_factor
        
        # setup GUI
        QtGui.QMainWindow.__init__(self)
        self.__setup_GUI()
        self.__connect_signals()

        # make initial plot and show it
        self.update()
        self.canv.show()
        self.show()

    def __add_doublespinboxes(self, layout, complex, label, number):
        """
        Add a new set of real/imag QDoubleSpinBox'es to given layout.
        Initial settings given by complex.
        Label should be a String for the label in front of the two boxes.
        """
        box_real = QtGui.QDoubleSpinBox()
        box_real.setMaximum(1e3)
        box_real.setMinimum(-1e3)
        box_real.setSingleStep(self.options.step)
        box_real.setValue(complex.real)
        layout.addWidget(QtGui.QLabel("%s %i real" % (label, number)))
        layout.addWidget(box_real)
        box_imag = QtGui.QDoubleSpinBox()
        box_imag.setMaximum(1e3)
        box_imag.setMinimum(-1e3)
        box_imag.setSingleStep(self.options.step)
        box_imag.setValue(complex.imag)
        layout.addWidget(QtGui.QLabel("imag"))
        layout.addWidget(box_imag)
        return box_real, box_imag


    def __setup_GUI(self):
        """
        Add matplotlib canvas, some boxs and stuff...
        """
        self.setWindowTitle("FitResp")
        self.setGeometry(300, 300, 500, 500)
        main = QtGui.QWidget()
        self.setCentralWidget(main)
        # add matplotlib canvas and setup layouts to put boxes in
        vlayout = QtGui.QVBoxLayout()
        vlayout.addStretch(1)
        main.setLayout(vlayout)
        canv = QMplCanvas()
        vlayout.addWidget(canv)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch(1)
        vlayout.addLayout(hlayout)

        # add some boxes
        self.boxes_poles_real = []
        self.boxes_poles_imag = []
        for i, pole in enumerate(self.paz['poles']):
            box_real, box_imag = self.__add_doublespinboxes(hlayout, pole,
                                                            "Pole", i + 1)
            self.boxes_poles_real.append(box_real)
            self.boxes_poles_imag.append(box_imag)
        self.boxes_zeros_real = []
        self.boxes_zeros_imag = []
        for i, zero in enumerate(self.paz['zeros']):
            box_real, box_imag = self.__add_doublespinboxes(hlayout, zero,
                                                            "Zero", i + 1)
            self.boxes_zeros_real.append(box_real)
            self.boxes_zeros_imag.append(box_imag)
        # add box for normalization factor
        box_norm = QtGui.QDoubleSpinBox()
        box_norm.setMaximum(1e10)
        box_norm.setMinimum(-1e10)
        box_norm.setSingleStep(self.options.step)
        box_norm.setValue(self.paz['gain'])
        hlayout.addWidget(QtGui.QLabel("Norm.Fac."))
        hlayout.addWidget(box_norm)
        self.box_norm = box_norm

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
        Connect box signals to methods...
        """
        connect = QtCore.QObject.connect
        for box in self.boxes_poles_real + self.boxes_poles_imag + \
                   self.boxes_zeros_real + self.boxes_zeros_imag + \
                   [self.box_norm]:
            connect(box, QtCore.SIGNAL("valueChanged(double)"),
                    self.on_anyButton_valueChanged)

    def update(self):
        """
        This method should do everything to update the plot.
        """
        # clear axes before anything else
        ax1 = self.ax1
        ax1.clear()
        ax2 = self.ax2
        ax2.clear()

        # plot theoretical responses from paz here
        paz = self.paz
        h, f = pazToFreqResp(paz['poles'], paz['zeros'], paz['gain'], 0.005,
                             16384, freq=True)
        ampl = abs(h)
        phase = np.unwrap(np.arctan2(-h.imag, h.real)) #take negative of imaginary part
        ax1.loglog(f, ampl, color="r")
        ax2.semilogx(f, phase, color="r", label='paz fit')

        # plot read in calibration output
        ax1.loglog(self.freq, self.ampl, color="b", ls="--")
        ax2.semilogx(self.freq, self.phase, color="b", ls="--", label='calibration output')

        ax2.legend()

        # update matplotlib canvas
        self.canv.draw()
    
    def on_anyButton_valueChanged(self, newvalue):
        for i, box in enumerate(self.boxes_poles_real):
            real = box.value()
            imag = self.paz['poles'][i].imag
            self.paz['poles'][i] = complex(real, imag)
        for i, box in enumerate(self.boxes_poles_imag):
            real = self.paz['poles'][i].real
            imag = box.value()
            self.paz['poles'][i] = complex(real, imag)
        for i, box in enumerate(self.boxes_zeros_real):
            real = box.value()
            imag = self.paz['zeros'][i].imag
            self.paz['zeros'][i] = complex(real, imag)
        for i, box in enumerate(self.boxes_zeros_imag):
            real = self.paz['zeros'][i].real
            imag = box.value()
            self.paz['zeros'][i] = complex(real, imag)
        self.paz['gain'] = self.box_norm.value()
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


def parse_paz_string(paz_string):
    """
    Parse a string representation of complex numbers separated by commas like
    "0j,0j,1+3.4j" to a list of complex numbers.
    """
    paz = paz_string.split(",")
    paz = map(complex, paz)
    return paz


def main():
    """
    Gets executed when the program starts.
    """
    usage = "Usage information goes here..."
    parser = optparse.OptionParser(usage)
    parser.add_option("-p", "--poles", type=str, dest="poles",
                      default="-0.0628332+0.0j,-206.69+0.0j",
                      help="Poles in a string separated by commas")
    parser.add_option("-z", "--zeros", type=str, dest="zeros", default="0j",
                      help="Zeros in a string separated by commas")
    parser.add_option("-n", "--normalization-factor", type=float,
                      dest="normalization_factor", default=206.0,
                      help="Normalization factor (A0)")
    parser.add_option("-s", "--step", type=float, dest="step", default=0.1,
                      help="Step size for SpinBoxes")
    parser.add_option("-f", "--file", type=str, dest="file", default="res_known",
                      help="Filename of relcalstack output to use as input.")
    (options, args) = parser.parse_args()

    qApp = QtGui.QApplication(sys.argv)
    myMainWindow = MyMainWindow(options)
    os._exit(qApp.exec_())


if __name__ == "__main__":
    main()
