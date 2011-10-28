import sys, math
import numpy as np
from def_act_sys_par import def_act_sys_par
from def_sys_par import def_sys_par
from freqDamp2paz import freqDamp2paz
from ltisim import ltisim
from quad import quad
from move import move

# search for minimum along new direction of decent

def mini(x, q, qn, d, delta, finac, data, ausf, einf,\
         m0, m1, m1c, m2, m2c, typ1_ges, typ2_ges,\
         param, nap, step, dt, npts,\
         x0, sr0, si0, resid0, residi0):
#    import ipdb; ipdb.set_trace()
    xl = np.zeros(nap)
    xr = np.zeros(nap)
    
    xm, qm = move(x, q, nap)
    for k in range(nap):
        xl[k] = x[k] - step * d[k]
        xr[k] = x[k] + step * d[k]
 #left
    amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
              def_act_sys_par(xl, param, delta, m1c, m2c) 
    sysl, m0_l, m1_l, m2_l = def_sys_par(x0, dt, m0, m1, m2,\
                                         amp, delay, sub, til,\
                                         typ1_ges, typ2_ges,\
                                         corn_freqs1, corn_freqs2, dmp)       
    sr, si, resid, residi =\
          freqDamp2paz(sysl, sr0, si0, resid0, residi0,\
                       m0_l, m1_l, m2_l)
    sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                 sr, si, resid, residi, m0_l, m1_l, m2_l, dt, npts)
    ql = quad(qn, sim, npts)
 #right
    amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
              def_act_sys_par(xr, param, delta, m1c, m2c)
    sysr, m0_r, m1_r, m2_r = def_sys_par(x0, dt, m0, m1, m2,\
                                         amp, delay, sub, til,\
                                         typ1_ges, typ2_ges,\
                                         corn_freqs1, corn_freqs2, dmp)
    sr, si, resid, residi =\
          freqDamp2paz(sysr, sr0, si0, resid0, residi0,\
                       m0_r, m1_r, m2_r)
    sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                 sr, si, resid, residi, m0_r, m1_r, m2_r, dt, npts)
    qr = quad(qn, sim, npts)

 #maximum?
    if ql < qm and qr < qm:
        print 'Maximum encountered! Try again with different start parameters!'
        sys.exit(1)

    while ql >= qm and qr >= qm and step >= 8. * finac:
        step = step / 8.
        for k in range(nap):
            xl[k] = xm[k] - step * d[k]                                   
            xr[k] = xm[k] + step * d[k]                                   
 #left   
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                  def_act_sys_par(xl, param, delta, m1c, m2c)       
        sysl, m0_l, m1_l, m2_l = def_sys_par(x0, dt, m0, m1, m2,\
                                             amp, delay, sub, til,\
                                             typ1_ges, typ2_ges,\
                                             corn_freqs1, corn_freqs2, dmp)       
        sr, si, resid, residi =\
                  freqDamp2paz(sysl, sr0, si0, resid0, residi0,\
                               m0_l, m1_l, m2_l)                    
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_l, m1_l, m2_l, dt, npts)       
        ql = quad(qn, sim, npts) 
 #right
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                  def_act_sys_par(xr, param, delta, m1c, m2c)       
        sysr, m0_r, m1_r, m2_r = def_sys_par(x0, dt, m0, m1, m2,\
                                             amp, delay, sub, til,\
                                             typ1_ges, typ2_ges,\
                                             corn_freqs1, corn_freqs2, dmp)       
        sr, si, resid, residi =\
                  freqDamp2paz(sysr, sr0, si0, resid0, residi0,\
                               m0_r, m1_r, m2_r)
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_r, m1_r, m2_r, dt, npts)       
        qr = quad(qn, sim, npts)
   
        if ql < qm and qr < qm:
             print 'Maximum encountered! Try again with different start parameters!'
             sys.exit(1)

 #witch side of the minimum?
    if ql < qm or qr < qm:
        if ql < qr:
 #turn around
            x, q = move(xl, ql, nap)
            xl, ql = move(xr, qr, nap)
            xr, qr = move(x, q, nap)
            for k in range(nap):
                d[k] = -d[k]
        if step > 1.:
            x, q = move(xr, qr, nap)
            axi = step

            return x, q, step, axi, amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp

        else:
            step = 2. * step
            xm, qm = move(xr, qr, nap)
            for k in range(nap):
                xr[k] = xm[k] + step * d[k]
 #right
            amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                      def_act_sys_par(xr, param, delta, m1c, m2c)           
            sysr, m0_r, m1_r, m2_r = def_sys_par(x0, dt, m0, m1, m2,\
                                                 amp, delay, sub, til,\
                                                 typ1_ges, typ2_ges,\
                                                 corn_freqs1, corn_freqs2, dmp)           
            sr, si, resid, residi =\
                      freqDamp2paz(sysr, sr0, si0, resid0, residi0,\
                                   m0_r, m1_r, m2_r)                            
            sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                         sr, si, resid, residi, m0_r, m1_r, m2_r, dt, npts)           
            qr = quad(qn, sim, npts)
             
            while qr < qm:            
                if step > 1.:
                    x, q = move(xr, qr, nap)                                   
                    axi = step
                          
                    return x, q, step, axi, amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp

                else:
                    step = 2. * step                                      
                    xm, qm = move(xr, qr, nap)                                 
                    for k in range(nap):                                  
                        xr[k] = xm[k] + step * d[k]
 #right
                amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                          def_act_sys_par(xr, param, delta, m1c, m2c) 
                sysr, m0_r, m1_r, m2_r = def_sys_par(x0, dt, m0, m1, m2,\
                                                     amp, delay, sub, til,\
                                                     typ1_ges, typ2_ges,\
                                                     corn_freqs1, corn_freqs2, dmp) 
                sr, si, resid, residi =\
                          freqDamp2paz(sysr, sr0, si0, resid0, residi0,\
                                       m0_r, m1_r, m2_r)               
                sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                             sr, si, resid, residi, m0_r, m1_r, m2_r, dt, npts)
                qr = quad(qn, sim, npts)

 #interpolate
        xi = (ql - qr) / (ql -2. * qm + qr) / 2. * step
        axi = np.abs(xi)
        for k in range(nap):
            x[k] = xm[k] + xi * d[k]
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                  def_act_sys_par(x, param, delta, m1c, m2c)
        sysp, m0_i, m1_i, m2_i = def_sys_par(x0, dt, m0, m1, m2,\
                                             amp, delay, sub, til,\
                                             typ1_ges, typ2_ges,\
                                             corn_freqs1, corn_freqs2, dmp)
        sr, si, resid, residi =\
                  freqDamp2paz(sysp, sr0, si0, resid0, residi0,\
                               m0_i, m1_i, m2_i)
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_i, m1_i, m2_i, dt, npts)
        q = quad(qn, sim, npts)

        return x, q, step, axi, amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp

    if step < 8.*finac:
        xi = (ql - qr) / (ql -2. * qm + qr) / 2. * step               
        axi = np.abs(xi)
        for k in range(nap):                                          
            x[k] = xm[k] + xi * d[k]                                  
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp, nap =\
                  def_act_sys_par(x, param, delta, m1c, m2c)    
        sysp, m0_i, m1_i, m2_i = def_sys_par(x0, dt, m0, m1, m2,\
                                             amp, delay, sub, til,\
                                             typ1_ges, typ2_ges,\
                                             corn_freqs1, corn_freqs2, dmp)   
        sr, si, resid, residi =\
                  freqDamp2paz(sysp, sr0, si0, resid0, residi0,\
                               m0_i, m1_i, m2_i)                
        sim = ltisim(0, data, ausf, einf, delay, sub, til,\
                     sr, si, resid, residi, m0_i, m1_i, m2_i, dt, npts)   
        q = quad(qn, sim, npts)

        return x, q, step, axi, amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp 
    
    print 'Residual error...'
    print 'Try again with other start parameters!'
    sys.exit(1)
