import sys, math
import numpy as np

# compute poles and zeros for the whole system;
# takes x0 as input and computes poles (sr, si)
# and zeros (resid, residi)

def freqDamp2paz(x0, sr, si, resid, residi, m0, m1, m2):
 #Poles
    for i in np.arange(1,m1+1,1):
        sr[m0+i] = -x0[m0+i]
        si[m0+i] = 0.

    for i in np.arange(1,m2+1,1):
        w = x0[m0+m1+i]
        h = x0[m0+m1+m2+i]
        wh = w * h
        whh = w * np.sqrt(1. - h**2)
        if h < 1:
            sr[m0+m1+i] = -wh
            si[m0+m1+i] = whh
            sr[m0+m1+m2+i] = -wh
            si[m0+m1+m2+i] = -whh
        else:
            sr[m0+m1+i] = -wh + whh
            si[m0+m1+i] = 0.
            sr[m0+m1+m2+i] = -wh - whh
            si[m0+m1+m2+i] = 0.
 #Zeros
    for i in np.arange(m0+1,m0+m1+2*m2+1,1):
        cresr = x0[0]
        cresi = 0.
        spowr = 1.
        spowi = 0.
        for k in np.arange(1,m0+1,1):
            spowre = spowr * sr[i] - spowi * si[i]
            spowi = spowr * si[i] + spowi * sr[i]
            spowr = spowre
            cresr = cresr + x0[k] * spowr
            cresi = cresi + x0[k] * spowi
        for k in np.arange(m0+1,m0+m1+2*m2+1,1):
            if k != i:
                 sdr = sr[i] - sr[k]
                 sdi = si[i] - si[k]
                 sdq = sdr * sdr + sdi * sdi
                 cresre = (cresr * sdr + cresi * sdi) / sdq
                 cresi = (cresi * sdr - cresr * sdi) / sdq
                 cresr = cresre
        resid[i] = cresr
        residi[i] = cresi
        
    return sr, si, resid, residi

