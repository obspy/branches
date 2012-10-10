#! /usr/bin/env python

"""

# RelCalTime.py is a program for the relative calibration of sensors
# in the time domane. The program simulates the answer of the unknown
# system to an excitation which is recorded in file1 (generator)and 
# compares it to the real output of the seismometer given in file2 (signal).
# To simulate the seismometer output various subsystems can be 
# defined by the following parameters:
# 
# Name          Type    CornerFreq    Damping
# ----------------------------------------------
#     --------1st order systems----------
# high pass     hp1        x             -
# low pass      lp1        x             -
#     --------2nd order systems----------
# high pass     hp2        x             x
# band pass     bp2        x             x
# low pass      lp2        x             x
#
# The excitation time series can be differentiated or integrated via
# removing or adding a zero at the origin in the transfer function
# The degree of differentiation or integration is given by the parameter m0
# (number of additional powers of s in the nominator):
#
#        integration:     m0 < 0
#        differentiation: m0 > 0
#
# Use m0 to make sure that excitation time series and instrument answer time
# series carry the same data type!
#
##########################################################################
# The program returns the corner frequencies and damping constants for
# each subsystem defined in the beginning and accordingly calculates the 
# poles. 
# According to the data type of the seismometer output given in the command
# line an adequate number of zeros at the origin is added for plotting the 
# transfer function. Only the velocity transfer function is plotted!

"""
import optparse
from RelCalTime import RelCalTime
from obspy.core import *
from CalcRespCalex import CalcResp
from plotRelCalTime import plotRelCalTime

usage = __doc__

parser = optparse.OptionParser(usage)

parser.add_option('-g', '--generator', type=str, dest='generator',
                    default='',
                    help='name of file containing generator data')
parser.add_option('-s', '--signal', type=str, dest='signal',
                    default='',
                    help='name of file containing signal data')
parser.add_option('-d', '--datatype', type=str, dest='datatype',
                    default='Vel',
                    help='data type defining signal unit (Vel, ACC)')
parser.add_option('-a', '--alias', type=float, dest='alias',
                    default=10.0,
                    help='corner freq of anti alias filter')
parser.add_option('--amp', type=str, dest='amp',
                    default='1.0+/-0.1',
                    help='amplitude ratio input/output')
parser.add_option('--delay', type=str, dest='delay',
                    default='0.0+/-0.001',
                    help='time delay between input an output')
parser.add_option('--sub', type=str, dest='sub',
                    default='0.0+/-0.0',
                    help='fraction of the input to substract from the output\
                    (correction for galvanic coupling, only if a halfbridge circuit was used)')
parser.add_option('--til', type=str, dest='til',
                    default='0.0+/-0.0',
                    help='estimated compansation for tilt of shaketable')
parser.add_option('--maxit', type=int, dest='maxit',
                    default=60,
                    help='maximum number of iterations')
parser.add_option('--qac', type=float, dest='qac',
                    default=1e-5,
                    help='minimum rms improvement')
parser.add_option('--finac', type=float, dest='finac',
                    default=1e-3,
                    help='maximum stepsize')
parser.add_option('--ns1', type=int, dest='ns1',
                    default=0,
                    help='start sample')
parser.add_option('--ns2', type=int, dest='ns2',
                    default=50000,
                    help='stop sample')
parser.add_option('--bw', type=float, dest='bw',
                    default=1.589e-6,
                    help='digitizer bit weight')
parser.add_option('--maxfreq', type=float, dest='maxfreq',
                    default=100.0,
                    help='maximum freq plotted in the transfer function')
parser.add_option('--plotTransFunc', dest='plotTransFunc',
                    default=True,
                    help='set False if you do not want the transfer function to be plotted')
parser.add_option('--switch', type=int, dest='switch',
                    default=0,
                    help='set 1 if you want each trace to be plotted on a single axis')

(options, args) = parser.parse_args()

file_name1 = options.generator
st1 = read(file_name1)
file_name2 = options.signal
st2 = read(file_name2)
samprate = st1[0].stats.sampling_rate

DataType = options.datatype
alias = options.alias
AMP = options.amp
DELAY = options.delay
SUB = options.sub
TIL = options.til
maxit = options.maxit
qac = options.qac
finac = options.finac
ns1 = options.ns1
ns2 = options.ns2

scaleFac = options.bw
maxFreq = options.maxfreq
PlotTransFunc = options.plotTransFunc
switch = options.switch

st_final, st_diff, poles, zeros = RelCalTime(st1, st2, DataType, alias,\
                                              AMP=AMP, DELAY=DELAY,\
                                              maxit=maxit, ns2=ns2)

scale = scaleFac
amp = float(AMP.split("+/-")[0])

plotRelCalTime(switch, scale, amp, st1, st2, st_final, st_diff)

if PlotTransFunc:
    CalcResp(poles, zeros, scaleFac, maxFreq, samprate)

