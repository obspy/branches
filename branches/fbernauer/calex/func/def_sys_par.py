import sys, math
import numpy as np

# create an array (syspar) containing the system parameters in the following shape:
#
# [ 0 | 0 |...| 0 | gain | fc1.1 |...| fc1.m1 | fc2.1 |...| fc2.m2 | dmp_1 |...| dmp_m2 | 0 |...]
#  >---(m0-1)----<   m0   >--------m1--------< >--------m2--------< >--------m2--------<

def def_sys_par(x0, dt, m0, m1, m2,\
                amp, delay, sub, til,\
                typ1, typ2,\
                corn_freqs1, corn_freqs2, dmp):
 #gain 
    gain = amp * dt
 #1st order
    for i in np.arange(0,m1,1):
        if typ1[i] == 'hp1':
            m0 = m0 + 1
        if typ1[i] == 'lp1':
            gain = gain * 2. * np.pi * corn_freqs1[i]

 #2nd order
    for i in np.arange(0,m2,1):
        if typ2[i] == 'hp2':
            m0 = m0 + 2
        if typ2[i] == 'bp2':
            m0 = m0 + 1
            gain = gain * 2. * np.pi * corn_freqs2[i]
        if typ2[i] == 'lp2':
            gain = gain * (2. * np.pi * corn_freqs2[i])**2

    for i in np.arange(0,m0,1):
        x0[i] = 0
    x0[m0] = gain
    for i in np.arange(0,m1,1):
        x0[m0+1+i] = 2. * np.pi * corn_freqs1[i]
    if m0 < 0:
        m0 = 0
        x0[m0] = gain
        for i in np.arange(0,m1,1):
            x0[1+i] = 2. * np.pi * corn_freqs1[i]
        m1 = m1 + 1
        x0[m1] = 0
    for i in np.arange(0,m2,1):
        x0[m0+m1+1+i] = 2. * np.pi * corn_freqs2[i]
        x0[m0+m1+m2+1+i] = dmp[i]
    
    return x0, m0, m1, m2

