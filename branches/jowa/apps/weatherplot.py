#!/usr/bin/env python
"""
USAGE: weatherplot.py inpath station
"""

import sys
import time
import datetime
import numpy as np
import math as m
import matplotlib
matplotlib.use("agg")
import matplotlib.colors as colors
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.transforms as mattrans
from obspy.core import UTCDateTime
from pytz import timezone



try:
    in_path = sys.argv[1]
    station = sys.argv[2]
except:
    print __doc__
    raise

try:
    tme = sys.argv[3]
    today = UTCDateTime(tme)
    t = UTCDateTime(tme)
except:
    t = datetime.datetime.today()
    today = UTCDateTime()

tu = t.hour
tl = today.hour
td = tu- tl


time_label = "Std 00:00:00 UTC (+%d Std Lokalzeit)"%(int (td))
in_file = "%s/%s.WSX.D.%02d%02d%02d.0000"%(in_path,station,today.day,today.month,today.year-2000)
outfile = "%s/%s_%02d%02d%02d_wet.png"%(in_path,station,today.day,today.month,today.year-2000)

def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type=='simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()


    a =  np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

def red_pressure(p,t,hum):    # After DWD
    g = 9.80665  #gravity
    R = 287.05   #Gasconst.
    a = 0.0065   #Temp.grad
    Ch = 0.12    #DWD const for including humidity
    h = 570      #height FFB
    T = 0        #Temp in Kelvin
    M = 0.0289644 #molar mass of air
    Eo = 6.11213
    pr = []

    lenP = len(p)
    for i in range(lenP): 
       # T = t[i] + 273
       T = t[i] + 273 + 0.00325 * h
       # E = hum[i]/100 * Eo * m.exp((17.5043 * T)/(241.2 + T))
       # pr[i] = p[i]*np.exp(g*h/(R*(T+Ch*E+a*h/2)))
       pr.append(p[i]*m.exp(g*h/(R*T)))
    return pr


f=open(in_file,"r");
ate = []
Dm = []
Sm = []
Pa = []
Ta = []
Ua = []
Rc = []
Ri = []
i = 0
d0 = 0;
dd = np.zeros(2*86400)
while 1:
    line = f.readline()
    if not line: break
    data = line.split(",")
    day = int(data[0][:2])
    mo = int(data[0][2:4])
    yr = 2000 + int(data[0][4:6])
    hr = int(data[1][:2])
    mn = int(data[1][2:4])
    sec = int(data[1][4:6])
    #import ipdb; ipdb.set_trace()
    xx = "%04d%02d%02d%02d%02d%02d"%(yr,mo,day,hr,mn,sec)
    if i == 0:
       x0 = "%04d%02d%02d%02d%02d%02d"%(yr,mo,day,0,0,0)
       d0 = UTCDateTime(x0)
    dd[i]  = ((UTCDateTime(xx) - d0)/3600.0)
    i += 1
    #ate.append(dd)
    
    name, value = data[5].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Dm.append(value)
    name, value = data[8].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Sm.append(value)
    name, value = data[13].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Pa.append(value)
    name, value = data[10].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Ta.append(value)
    name, value = data[12].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Ua.append(value)
    name, value = data[14].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Rc.append(value)
    name, value = data[16].split('=')
    unit = value.strip("0123456789.")
    value = value.strip("#abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    value = float(value)
    Ri.append(value)
    name, stat = data[26].split('=')
    stat = stat.strip(" ")
    label = "%04d-%02d-%02d Wetterdaten Station %s"%(yr,mo,day,stat)

     
n = 180
MDm = moving_average(Dm, n, type='simple')
MSm = moving_average(Sm, n, type='simple')
MPa = moving_average(Pa, n, type='simple')
MTa = moving_average(Ta, n, type='simple')
MUa = moving_average(Ua, n, type='simple')
MRc = moving_average(Rc, n, type='simple')
MRi = moving_average(Ri, n, type='simple')
MPr = red_pressure(MPa,MTa,MUa)
LPr = MPr[i-1]
LDm = MDm[i-1] 
LSm = MSm[i-1] 
LPa = MPa[i-1] 
LTa = MTa[i-1] 
LUa = MUa[i-1] 
LRc = Rc[i-1] 
LRi = MRi[i-1] 
LPr = MPr[i-1] 


dx = np.resize(dd,i)
Lx = dx[i-1]
#import ipdb; ipdb.set_trace()

fig = plt.figure()
ax1 = fig.add_subplot(321)

ax1.set_title(label);
p1, = ax1.plot(dx,MUa,'b-',label = 'rel. Luftfeuchte')
ax1.text(Lx, LUa, '%.1f' % (float(LUa)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax1.set_ylabel('[%]',color='b')
ax1.set_xlim(0,24)
ax1.set_ylim(0,100)
for tl in ax1.get_yticklabels():
    tl.set_color('b')

lines = [p1]
leg1 = ax1.legend(lines,[l.get_label() for l in lines],'lower left')
for t in leg1.get_texts():
    t.set_fontsize('x-small')

ax2 = fig.add_subplot(322)
p2, =ax2.plot(dx,MRc,'b-',label = 'kum. Niederschlag')
ax2.text(Lx, LRc, '%.2f' % (float(LRc)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax2.set_ylabel('[mm]',color='b')
ax2.set_xlim(0,24)
if max(MRc) < 100:
   ax2.set_ylim(0,100)
else:
   ax2.set_ylim(0)
for tl in ax2.get_yticklabels():
    tl.set_color('b')

ax3 = ax2.twinx()
p3, =ax3.plot(dx,MRi,'r-',label='Niederschlagsrate')
ax3.text(Lx, LRi, '%.1f' % (float(LRi)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax3.set_ylabel('[mm/std]',color='r')
ax3.set_xlim(0,24)
if max(MRi) < 50:
   ax3.set_ylim(0,50)
else:
   ax3.set_ylim(0)

for tl in ax3.get_yticklabels():
    tl.set_color('r')

lines = [p2,p3 ]
leg2 = ax2.legend(lines,[l.get_label() for l in lines],'upper left')
for t in leg2.get_texts():
    t.set_fontsize('x-small')

ax4 = fig.add_subplot(323)
p4, = ax4.plot(dx,MTa,'b-',label='Lufttemperatur')
ax4.text(Lx, LTa, '%.1f' % (float(LTa)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax4.set_ylabel('[C]',color='b')
ax4.set_xlim(0,24)
ax4.set_ylim(-30,40)
for tl in ax4.get_yticklabels():
    tl.set_color('b')

lines = [p4]
leg4 = ax4.legend(lines,[l.get_label() for l in lines],'lower left')
for t in leg4.get_texts():
    t.set_fontsize('x-small')



ax5 = fig.add_subplot(324)
p5, =ax5.plot(dx,MPr,'b-',label='red. Luftdruck')
ax5.text(Lx, LPr, '%.1f' % (float(LPr)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax5.set_ylabel('',color='b')
ax5.set_xlim(0,24)
ax5.set_ylim(950,1050)
for tl in ax5.get_yticklabels():
    tl.set_color('b')

ax6 = ax5.twinx()
p6, =ax6.plot(dx,MPa,'r-',label='abs. Luftdruck')
ax6.text(Lx, LPa, '%.1f' % (float(LPa)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax6.set_ylabel('[hPa]',color='r')
ax6.set_xlim(0,24)
ax6.set_ylim(910,1010)
for tl in ax6.get_yticklabels():
    tl.set_color('r')

lines = [p5,p6 ]
leg5 = ax5.legend(lines,[l.get_label() for l in lines],'lower left')
for t in leg5.get_texts():
    t.set_fontsize('x-small')



ax7 = fig.add_subplot(325)
p7, =ax7.plot(dx,MSm,'b-',label='Windgeschwindigkeit')
ax7.set_xlabel(time_label)
ax7.text(Lx, LSm, '%.1f' % (float(LSm)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax7.set_ylabel('[m/s]', color='b')
ax7.yaxis.set_ticks_position('left')
ax7.yaxis.set_label_position('left')
ax7.set_xlim(0,24)
for tl in ax7.get_yticklabels():
    tl.set_color('b')

lines = [p7 ]
leg7 = ax7.legend(lines,[l.get_label() for l in lines],'lower left')
for t in leg7.get_texts():
    t.set_fontsize('x-small')


ax8 = fig.add_subplot(326)
p8, =ax8.plot(dx,MDm,'b-', label='Windrichtung',bbox=dict(facecolor='white', alpha=0.2))
ax8.text(Lx, LDm, '%.1f' % (float(LDm)),bbox=dict(facecolor='white', alpha=0.2),ha="right")
ax8.set_ylabel('[deg]',color='b')
ax8.set_xlim(0,24)
ax8.set_ylim(0,360)
ax8.set_xlabel(time_label)
ax8.yaxis.set_ticks_position('left')
ax8.yaxis.set_label_position('left')
for tl in ax8.get_yticklabels():
    tl.set_color('b')

lines = [p8 ]
leg8 = ax8.legend(lines,[l.get_label() for l in lines],'lower left')
for t in leg8.get_texts():
    t.set_fontsize('x-small')

plt.savefig(outfile,dpi=92,format='png')

import os
import Image

f, e = os.path.splitext(outfile)
out = f + ".gif"
if out != outfile:
    try:
        Image.open(outfile).save(out)
    except IOError:
        print "cannot convert", outfile

outfile2 = "/bay200/earthworm/WWWG/%s/%04d/%s_%02d%02d%02d_wet.gif"%(station,today.year,station,today.day,today.month,today.year-2000)
outfile3 = "/bay200/earthworm/WWWG/MONITOR/%s_wet.gif"%(station)
os.system ("cp %s %s" % (out, outfile2))
os.system ("cp %s %s" % (out, outfile3))
