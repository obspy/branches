import sys, math
import numpy as np
from obspy.core import *
from def_sys_par import def_sys_par
from freqDamp2paz import freqDamp2paz
from rekf1 import rekf1
from rekf2 import rekf2
from politrend import politrend
from ltisim import ltisim
#from ltisim_c import ltisim

eing_st = read('../BW.M1GE..EHZ.2011.073')
eing = eing_st[0]
einf_st = read('../BW.M1GE..EHZ.2011.073.f.msd')
einf = einf_st[0].data
ausf_st = read('../BW.M1SI..EHZ.2011.073.f.msd')
ausf = ausf_st[0].data
for st in eing_st, einf_st, ausf_st:
    for tr in st:
        tr.data = tr.data.astype(np.float64)

syspar0 = np.zeros(30)
sr0 = np.zeros(30)
si0 = np.zeros(30)
resid0 = np.zeros(30)
residi0 = np.zeros(30)
npts = eing.stats.npts
dt = 0.005
amp = 0.02
delay = 0.
sub = 0.
til = 0
m0_ges =  0
m1_ges =  1
m2_ges =  3
typ1_ges =  ['lp1']
typ2_ges =  ['bp2', 'lp2', 'lp2']
corn_freqs1_ges =  [10.0]
corn_freqs2_ges =  [1.0, 10.0, 10.0]
dmp_ges =  [0.59999999999999998, 0.3090169943749474, 0.80901699437494745]

syspar_ges, m0_sim, m1_sim, m2_sim =\
        def_sys_par(syspar0, dt, m0_ges, m1_ges, m2_ges,\
                    amp, delay, sub, til,\
                    typ1_ges, typ2_ges,\
                    corn_freqs1_ges,\
                    corn_freqs2_ges, dmp_ges)

sr_sta, si_sta, resid_sta, residi_sta =\
        freqDamp2paz(syspar_ges, sr0, si0, resid0, residi0,\
                     m0_sim, m1_sim, m2_sim)

diff = ltisim(0, eing.data, ausf, einf, delay, sub, til,\
              sr_sta, si_sta, resid_sta,\
              residi_sta, m0_sim, m1_sim, m2_sim, dt, npts)
