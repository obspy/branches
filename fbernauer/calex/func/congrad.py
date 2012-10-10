import sys, math
import numpy as np
from def_act_sys_par import def_act_sys_par
from def_sys_par import def_sys_par
from freqDamp2paz import freqDamp2paz
from ltisim import ltisim
from quad import quad
from mini import mini

# Calculate partial derivatives at point x and
# find new direction of decent dd

def congrad(niter, mp, nap, x, q, qn, finac, delta, data, ausf, einf,\
            m0, m1, m1c, m2, m2c, typ1_ges, typ2_ges, gnorm, step, dt, npts,\
            param, x0, sr0, si0, resid0, residi0):
    g = np.zeros(nap)
    d = np.zeros(nap)
    dd = np.zeros(nap)
    
 #partial derivatives
    for k in range(nap):
        x[k] = x[k] + finac
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
              def_act_sys_par(x, param, delta, m1c, m2c)
        #print 'corn_freqs1', corn_freqs1
        #print 'corn_freqs2', corn_freqs2
        #print 'dmp', dmp
        syspar_p, m0_p, m1_p, m2_p = def_sys_par(x0, dt, m0, m1, m2,\
                                                 amp, delay, sub, til,\
                                                 typ1_ges, typ2_ges,\
                                                 corn_freqs1, corn_freqs2, dmp)
        sr, si, resid, residi =\
              freqDamp2paz(syspar_p, sr0, si0, resid0, residi0,\
                           m0_p, m1_p, m2_p)
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_p, m1_p, m2_p, dt, npts)
        q_p = quad(qn, sim, npts)
 
        x[k] = x[k] - finac - finac

        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
              def_act_sys_par(x, param, delta, m1c, m2c)
        syspar_m, m0_m, m1_m, m2_m = def_sys_par(x0, dt, m0, m1, m2,\
                                                 amp, delay, sub, til,\
                                                 typ1_ges, typ2_ges,\
                                                 corn_freqs1, corn_freqs2, dmp)
        sr, si, resid, residi =\
              freqDamp2paz(syspar_m, sr0, si0, resid0, residi0,\
                           m0_m, m1_m, m2_m)
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_m, m1_m, m2_m, dt, npts)
        q_m = quad(qn, sim, npts)

        x[k] = x[k] + finac      
        g[k] = (q_p - q_m) / 2. / finac

 #new direction of decent
    if np.mod(niter, nap) == 0:
        gnorm = 0.
        for k in range(nap):
            gnorm = gnorm + g[k]**2       
            d[k] = -g[k]
    else:
        ga = gnorm
        gnorm = 0.
        for k in range(nap):
            gnorm = gnorm + g[k]**2
        beta = gnorm / ga
        for k in range(nap):
            d[k] = -g[k] + beta * d[k]
    dlen = 0.
    for k in range(nap):
        dlen = dlen + d[k]**2
    dlen = np.sqrt(dlen)
    for k in range(nap):
        dd[k] = d[k] / dlen
    
    x, q, step, axi, amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp =\
                  mini(x, q, qn, dd, delta, finac, data, ausf, einf,\
                       m0, m1, m1c, m2, m2c, typ1_ges, typ2_ges,\
                       param, nap, step, dt, npts,\
                       x0, sr0, si0, resid0, residi0)

    return x, q, d, sim, step, axi, gnorm, \
           amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp

