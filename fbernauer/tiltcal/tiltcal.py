###################################################
# method for absolute calibration of seismometers #
# according to tiltcal5 by E.Wieland.             #
###################################################

import sys
import numpy as np
from flcoef import *
from rekfl import rekfl
from krum import krum
from heapsort2 import heapsort
from politrend import politrend
from politrendTilt import politrendTilt
from integrate import integrate
from trend import trend
from zspline import zspline
from mspline import mspline
from differentiate import differentiate
from step import step
import matplotlib.pyplot as plt


def tiltcal(data, samprate, fcs, hs, gap, volts, tilt, bfc=0.0, bm=0):
    
    dt = 1.0 / samprate
    npts = len(data)
    npol = 3
    perc1 = 50
    perc2 = 95
    fac = volts / tilt * 0.001
    # remove offset using the first 6 seconds that have to be quiet!
    z = np.ones(npts)
    offset = np.sum(data[0:int(6.0*samprate)])
    data = data - offset

    # apply butterworth low pass filter if required
    if bfc > 0.0 and bm > 0:
        bt0 = 1.0 / bfc
        mm = int(bm / 2.0)

        # if odd order apply first order low pass
        if bm > 2 * mm:
            f0_lp1, f1_lp1, f2_lp1, g1_lp1, g2_lp1 = lp1(bt0*samprate)
            data = rekfl(data, npts, f0_lp1, f1_lp1, f2_lp1, g1_lp1, g2_lp1)

        # now apply second order low pass
        for i in range(mm):
            h = np.sin(np.pi / 2.0 * (2.0 * i - 1.0) / bm)
            f0_lp2, f1_lp2, f2_lp2, g1_lp2, g2_lp2 = lp2(bt0*samprate, h)
            data = rekfl(data, npts, f0_lp2, f1_lp2, f2_lp2, g1_lp2, g2_lp2)

        # report filtering
        print 'Input data filtered with low pass Butterworth filter:'
        print '         corner frequency: ' + str(bfc) + 'Hz'
        print '         order: ' + str(bm) + '.'

    raw = data.copy()
    # deconvolution to ground acceleration
    # done by appling an exact invers second order high pass filter (infinit period)
    t0 = 1.0e12
    h = 1.0
    t0s = 1.0 / fcs

    f0_he2, f1_he2, f2_he2, g1_he2, g2_he2 = he2(t0/dt, t0s/dt, h, hs)
    data = rekfl(data, npts, f0_he2, f1_he2, f2_he2, g1_he2, g2_he2)
    data = politrend(npol, data, npts, z)

    x = data.copy()
    deconv_vel = data.copy()
    np.savetxt('tiltcal_vel.txt', deconv_vel)
    
    # differentiate to get ground acceleration
    data_diff = differentiate(data, npts, dt, 1)
    #np.savetxt('diff_test', data_diff)

    # loop over fife trial values if no gap is given
    if gap > 0.0:
        onegap = True
        ngap = 1
    else:
        gap = 0.125
        onegap = False
        ngap = 5

    for k in range(ngap):
        avglen = 6.0 * gap
        iab = int(gap / dt)
        iavg = int(avglen / dt)
        data = x
        z = np.ones(npts)
        P0 = np.zeros(npts)
        y = np.zeros(npts)

        ja = np.ones(99)

        # search for quiet section of minimum length 2*iab+1 samples
        P = krum(data, npts, 2*iab+1, P0)
        for j in range(npts):
            P[j] = np.log10(max(P[j], 1.0e-6))
        P1 = P.copy()

#        import ipdb; ipdb.set_trace()
        z = heapsort(npts, P1)
        n50 = int(perc1 * npts / 100.0)
        n95 = int(perc2 * npts / 100.0)

        zlim = 0.5 * (z[n50] + z[n95])
        P = P - zlim
        z = z - zlim
        

    # create trigger z = 0 if quiet, z = 1 if pulse
        for j in range(npts):
            if P[j] < 0:
                z[j] = 1.0
            else:
                z[j] = 0.0

        #zn1 = z[npts-1]
        #zn = z[n]
        #z[n-1] = -0.4
        #z[n] = 1.4
        #z[n-1] = zn1
        #z[n] = zn
        
        mpol = npol - 2
        if mpol < 1:
            print 'npol too small!'
            sys.exit(1)

        # compute residual signal
        data2 = data_diff.copy()
        quiet = differentiate(data2, npts, dt, 0)

        quiet = quiet * z

        res, a = politrendTilt(npol, quiet, npts, z)
        res = res * z
        
        res_int = integrate(res, npts, dt)
        
        np.savetxt('tiltcal_res.txt', res_int)

        # final trend removal on acceleration signal
        xpolint = 0.0
        xavg = 0.0
        for i in range(npts):
            xpol = a[mpol]
            for j in np.arange(mpol-1, 0, -1):
                xpol = xpol * (float(i + 1) / fnh - 1.0) + a[j]
            xpolint = xpolint + xpol * dt
            data_diff[i] = data_diff[i] - xpolint
            xavg = xavg + data_diff[i]
        xavg = xavg / npts
        for i in range(npts):
            data_diff[i] = data_diff[i] - xavg

        acc = data_diff.copy()
        np.savetxt('tiltcal_acc.txt', acc)

        data_c = data_diff.copy()

        # identifiy pulses
        number = 0
        i = 0
        while i < npts and z[i] < 0.5:
            i = i + 1
        n1 = i

        while i < npts and z[i] > 0.5:
            i = i + 1
        n2 = i - 1
        
        if i == npts:
            print 'No pulses found! Check dispcal.??? for pulses!'
            sys.exit(1)
        
        # continue if interval is too small (< gap)
        while n2 < n1 + iab:
            while i < npts and z[i] < 0.5:
                i = i + 1
            n1 = i

            while i < npts and z[i] > 0.5:
                i = i + 1
            n2 = i - 1
        # now we have the first (n1) and the last (n2) sample of the first quiet interval
        
            if i == n:
                print 'No pulses found! Check dispcal.??? for pulses!'
                sys.exit(1)
        
        # now continue with the next pulses
        steps = []
        marks = []
        while i < npts:
            while i < npts and z[i] < 0.5:
                i = i + 1
            if i == npts: break
            n3 = i

            while i < npts and z[i] > 0.5:
                i = i + 1
            if i == npts: break
            n4 = i - 1

            # continue if interval is too small (< gap)
            while n4 < n3 + iab:
                while i < npts and z[i] < 0.5:
                    i = i + 1
                if i == npts: break
                n3 = i

                while i < npts and z[i] > 0.5:
                    i = i + 1
                if i == npts: break
                n4 = i - 1
            # now we have the first (n1) and the last (n2) sample of the next quiet interval
            number = number + 1
            
            #if number == 1:
            #    data_c = zspline('zsp', 1, n2, n3, npts, data_c, npts)
            #    n2null = n2
            #elif n4 >= n3+iab:
            #    #print 'bin da!'
            #    data_c = zspline('zsp', n1, n2, n3, npts, data_c, npts)
            #n3null = n3

            marks.append((n2,n3-1))
            print 'found pulse # ' + str(number) + ': from sample ' + str(n2) + ' to sample ' + str(n3 - 1)
            
            n1a = 0
            n2a = n2 - n1 
            n3a = n3 - n1 
            n4a = n4 - n1
            n1a = max(n1a, n2a-iavg)
            n4a = min(n4a, n3a+iavg)
            for ii in range(n4a):
                y[ii] = data_diff[n1-1+ii]
            
            #print n1a, n2a, n3a, n4a

            y_m = mspline('msp', n1a, n2a, n3a, n4a, y, n4a)
            #y_int = integrate(y_z, npts, dt)
            #y_int = cumtrapz(y_z) * dt
            stp = step(y_m, n1a, n2a, n3a, n4a, n4a)


            n1 = n3
            n2 = n4

            steps.append(stp)
            
        
            #np.savetxt('y_z'+str(number), y_z)
            #np.savetxt('y_int'+str(number), y_int)
        #print steps

        #dtr = trend('tre', 0, n2-n1+1, 0, 0, data_c[n1:], npts-n1)
        #for i in np.arange(n1, npts, 1):
        #    data_c[i] = dtr[i-n1]
        #
        #y = data_c * z
        #ymin = 0.0
        #ymax = 0.0
        #for i in np.arange(n2null+1, n3null-1,1):
        #    ymin = min(ymin,y[i])
        #    ymax = max(ymax,y[i])
        #for i in range(n2null):
        #    y[i] = min(ymax, max(ymin, y[i]))
        #for i in np.arange(n3null, npts, 1):
        #    y[i] = min(ymax, max(ymin, y[i]))
        #
        #
        #y_dis = integrate(data_c, npts, dt)
        
        # remove offset from displacement
        #offset =  np.mean(y_dis)
        #y_dis = y_dis - offset
        #displ = y_dis.copy()

        ##############################################################
        # Statistics
        total = sum(np.abs(steps))
        avgs = total / number
        
        sigma = np.std(np.abs(steps))
        
        print ''
        print '-------------------------------------------------------------'
        print 'Raw average step: ' + str(np.round(avgs,3)) + ' +/- ' + str(np.round(sigma, 3))
        
        print 'Raw generator constant: ' + str(np.round((avgs * fac) * 1e6,3)) + ' +/- ' + str(np.round((sigma * fac) *1e6, 3)) + 'Vs/m'
        print '-------------------------------------------------------------'
        if number <= 2:
            return raw, deconv, displ, marks
        
        
#        import ipdb; ipdb.set_trace()
        ja = np.ones(len(steps))
        for nrest in np.arange(number-1,int(float(number+1.0)/2.0),-1):
            siga = sigma
            kmax = np.argmax(steps)
            ja[kmax] = 0
            total = 0
            #for k in range(number):
            #    total = total + ja[k] * steps[k]
            stepsa = ja * steps
            total = sum(np.abs(stepsa))
            #print total
            avgs = total / nrest
            #print avgs
            total = 0
            for k in range(number):
                total = total + ja[k] * (abs(steps[k]) - avgs)**2
            sigma = np.sqrt(total / nrest)
            
            print 'Pulse ' + str(kmax) + ' eliminated; ' + str(nrest) + ' pulses remaning: ' + str(np.round((avgs * fac) * 1e6,3)) + ' +/- ' + str(np.round((sigma * fac) *1e6, 3)) + 'Vs/m'
            
#            if sigma < 0.05*avgs and siga-sigma < siga/ nrest: break
            steps[kmax] = 0.0
        print '------------------------------------------------------------'
        print ''
        
        gap = gap * 2.0
        return raw, deconv_vel, acc, marks
