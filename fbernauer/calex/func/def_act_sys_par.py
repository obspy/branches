import sys, math
import numpy as np

def def_act_sys_par(x, param, delta, m1, m2):
    mp = len(param)
    xx = np.zeros(mp)
    nap = 0
    corn_freqs1 = np.zeros(m1)
    corn_freqs2 = np.zeros(m2)
    dmp = np.zeros(m2)
    for i in range(mp):
        if delta[i] > 0.:
            nap = nap + 1
            xx[i] = param[i] + x[nap-1] * delta[i]
        else:
            xx[i] = param[i]
    amp = xx[0]
    delay = xx[1]
    sub = xx[2]
    til = xx[3]
    for i in range(m1):
        corn_freqs1[i] = xx[4+i]
    for i in range(m2):
        corn_freqs2[i] = xx[4+m1+2*i]
        dmp[i] = xx[4+m1+2*i+1]

    return amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap  
  
