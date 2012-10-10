#! /usr/bin/env python

##################################
# Based on calex5a by E. Wieland #
##################################

# RelCalTime.py is a program for the relative calibration of sensors
# in the time domane. The program simulates the answer of the unknown
# system to an excitation which is recorded in file1 and compares it
# to the real output of the seismometer given in file2.
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
# removing or adding a zero at the origin in the transfer function.
# The degree of differentiation or integration is given by the parameter m0:
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
# Example:
# The output of an STS2 is proportional to velocity; so two zeros at the origin
# are added in the transfer function.


"""
USAGE:   RelCalTime.py (st1, st2, DataType, alias, 
                        AMP, DELAY, SUB, TIL,
                        maxit, qac, finac, ns1, ns2)

file1:   stream with excitation data
file2:   stream with instrument answer data
DataType:data type of instrument output:
         Dsp - displacement
         Vel - velocity
         Acc - acceleration
alias:   corner freq of anti alias filter [Hz]
AMP  :   estimated amplitude ratio between input and output, Format: <amp/delta>
DELAY:   estimated time delay between input and output, Format: <delay/delta> 
SUB  :   fraction of the input to substract from the output, Format: <sub/delta>
         (correction for galvanic coupling, only if a halfbridge circuit was used)
TIL  :   estimated compansation for tilt of shaketable, Format: <til/delta>
maxit:   maximum number of iterations (has to be int)
qac  :   minimum rms improvement 
finac:   maximum stepsize 
ns1  :   number of start sample (has to be int)
ns2  :   number of stop sample (has to be int)

"""


import sys, math
import numpy as np
from obspy.core import *
from matplotlib.pylab import *
from def_sys_par import def_sys_par
from def_act_sys_par import def_act_sys_par
from freqDamp2paz import freqDamp2paz
from rekf1 import rekf1
from rekf2 import rekf2
from politrend import politrend
from ltisim import ltisim
from quad import quad
from move import move
from congrad import congrad
from mini import mini
from CalcRespCalex import CalcResp

#if len(sys.argv) < 15:
#   print __doc__
#   sys.exit(1)

def RelCalTime(st1, st2, DataType, alias,\
               AMP='0.+/-0.', DELAY='0.+/-0.', SUB='0.+/-0.', TIL='0.+/-0.',\
               maxit=100, qac=1e-5, finac=1e-3, ns1=0, ns2=60000):

    ########################################################
    # For writing comunication not only to stdout but also
    # to the file "calex.out" a new write method is
    # defined.
    class SplitWriter():
        """ 
        Implements a write method that writes a given message on all children
        """
        def __init__(self, filehandle):
            """ 
            Remember provided objects as children.
            """
            self.file = filehandle
            self.stdout = sys.stdout
    
        def write(self, msg):
            """ 
            Sends msg to all childrens write method.
            """
            self.stdout.write(msg)
            self.file.write(msg)
   
   
    f = open("RelCalTime.out", "wt")
    sys.stdout = SplitWriter(f)
    
    
    ########################################################                      
    # read input
    
    eing_st = st1
    if len(eing_st) > 1:
        print 'more than one traces found in stream 1!'
        f.close()
        sys.exit(1)
    eing = eing_st[0]
    
            
    ausg_st = st2
    if len(ausg_st) > 1:
        print 'more than one traces found in stream 2!'
        f.close()
        sys.exit(1)
    ausg = ausg_st[0]
    
    # make sure that the stype is what cython expects later!
    for tr in eing, ausg:
        tr.data = tr.data.astype(np.float64)
    
    ##########################################################                  
    # The arrays with raw data are now stored in eing.data / #                  
    # ausg.data                                              #                  
    ########################################################## 
    
    #########################################################
    # read input parameters - from command line
    #DataType = sys.argv[3]
    #alias = float(sys.argv[4])
    #AMP = sys.argv[5]
    #DELAY = sys.argv[6]
    #SUB = sys.argv[7]
    #TIL = sys.argv[8]
    #maxit = int(sys.argv[9])
    #qac = float(sys.argv[10])
    #finac = float(sys.argv[11])
    #ns1 = int(sys.argv[12])
    #ns2 = int(sys.argv[13])
    #MaxPer = float(sys.argv[14])
    
    if DataType not in ('Dsp', 'Vel', 'Acc'):
        print 'Data type not recognized! Has to be "Dsp", "Vel" or "Acc"!'
        sys.exit(1)
    
    param = []
    delta = []
    name = []
    amp = float(AMP.split("+/-")[0])
    param.append(amp)
    damp = float(AMP.split("+/-")[1])
    delta.append(damp)
    name.append('amp')
    delay = float(DELAY.split("+/-")[0])
    param.append(delay)
    ddelay = float(DELAY.split("+/-")[1])
    delta.append(ddelay)
    name.append('delay')
    sub = float(SUB.split("+/-")[0])
    param.append(sub)
    dsub = float(SUB.split("+/-")[1])
    delta.append(dsub)
    name.append('sub')
    til = float(TIL.split("+/-")[0])
    param.append(til)
    dtil = float(TIL.split("+/-")[1])
    delta.append(dtil)
    name.append('til')
    
    samprate_eing = eing.stats.sampling_rate
    samprate_ausg = ausg.stats.sampling_rate
    
    if samprate_eing != samprate_ausg:
        print 'Sampling of input and output is inconsistent!'
        f.close()
        sys.exit(1)
    
    samprate = samprate_ausg
    dt = 1/samprate
    npts = ns2 - ns1
    
    # create new miniseed header
    stats = {'network': ausg.stats.network,\
             'station': ausg.stats.station,\
             'location': '',\
             'channel': ausg.stats.channel,\
             'npts': npts,\
             'sampling_rate': samprate,\
             'starttime': ausg.stats.starttime+ns1/samprate ,\
             'mseed' : {'dataquality' : 'D'}}
    
    t = np.linspace(ns1,ns2,num=npts,endpoint='true')*dt
    
    # system start parameters
    typ1_sta = []
    corn_freqs1_sta = []
    delta_corn_freqs1_sta = []
    typ2_sta = []
    corn_freqs2_sta = []
    delta_corn_freqs2_sta = []
    dmp_sta = []
    delta_dmp_sta = []
    
    m0_sta = int(raw_input("Give number of additional"\
                           " powers of s in nominator: "))
    
    m1_sta = int(raw_input("Give number of 1st order subsystems: "))
    
    for i in np.arange(0,m1_sta,1):
        Type1, F, Df = str(raw_input("Give type of 1st"\
                                         " order system nr. "+str(i+1)+": ")),\
                           float(raw_input("Give start value for corner period"\
                                           " of subsystem nr. "+str(i+1)+": ")),\
                           float(raw_input("and now its estimated uncertainty: "))
    
        if Type1 in ('hp1','lp1'):
            typ1_sta.append(Type1)
            corn_freqs1_sta.append(F)
            delta_corn_freqs1_sta.append(Df)
        else:
            print 'Wrong system type! Must be <hp1> or <lp1>!'
            f.close()
            sys.exit(1)
    
    m2_sta = int(raw_input("Give number of 2nd order subsystems: "))
    
    for i in np.arange(0,m2_sta,1):
        Type2, F, Df = str(raw_input("Give type of 2nd"\
                                         " order system nr. "+str(i+1)+": ")),\
                           float(raw_input("Give start value for corner period"\
                                           " of subsystem nr. "+str(i+1)+": ")),\
                           float(raw_input("and now its estimated uncertainty: "))
    
        Dmp, Ddmp = float(raw_input("Give start value for damping"\
                                    " constant of subsystem nr. "+str(i+1)+": ")),\
                    float(raw_input("and now its estimated uncertainty: "))
    
        if Type2 in ('hp2','bp2','lp2'):
            typ2_sta.append(Type2)
            corn_freqs2_sta.append(F)
            delta_corn_freqs2_sta.append(Df)
            dmp_sta.append(Dmp)
            delta_dmp_sta.append(Ddmp)
        else:
            print 'Wrong system type! Must be <hp2>, <bp2> or <lp2>!'
            f.close()
            sys.exit(1)
    m1a = len(corn_freqs1_sta)
    m2a = len(corn_freqs2_sta)
    
    ##########################################################
    # Print start parameters
    print ''
    print 'System start parameters:'
    print '------------------------'
    print 'amp: ', amp, ' +/-', damp
    print 'del: ', delay, ' +/-', ddelay
    print 'sub: ', sub, ' +/-', dsub
    print 'til: ', til, ' +/-', dtil
    
    if m1_sta > 0:
        for i in np.arange(0,m1_sta,1):
            print ''
            print '1st order subsystem nr. ' + str(i+1) + \
                  ':' + ' ' + str(typ1_sta[i])
            print 'per: ', corn_freqs1_sta[i], ' +/-',\
                   delta_corn_freqs1_sta[i]
    if m2_sta > 0:
        for i in np.arange(0,m2_sta,1):
            print ''
            print '2nd order subsystem nr. ' + str(i+1) +\
                  ':' + ' ' + str(typ2_sta[i])
            print 'per: ', corn_freqs2_sta[i],\
                  ' +/-', delta_corn_freqs2_sta[i]
            print 'dmp: ', dmp_sta[i], ' +/-', delta_dmp_sta[i]
    print '------------------------'
    
    ##########################################################
    # Preparation of data
    eing.data = eing.data[ns1:ns2]
    ausg.data = ausg.data[ns1:ns2]
    
    # Anti alias-filter
    syspar0 = np.zeros(30)
    sr0 = np.zeros(30)
    si0 = np.zeros(30)
    resid0 = np.zeros(30)
    residi0 = np.zeros(30)
    
    m_alias = int(6. / np.log10((1. / alias) / dt) + 1.)
    n_alias = int(floor(m_alias / 2))
    
    m1_alias = 0
    typ1_alias = []
    corn_freqs1_alias = []
    
    for i in range(m1a):
        param.append(corn_freqs1_sta[i])
        delta.append(delta_corn_freqs1_sta[i])
        number = str(i+1)
        name.append('Fc1['+number+']')
    
    if m_alias > 2 * n_alias:
        m1_alias = 1
        typ1_alias.append('lp1')
        corn_freqs1_alias.append(alias)
        param.append(alias)
        delta.append(0.)
        name.append('F1ali')
    
    for i in range(m2a):
        param.append(corn_freqs2_sta[i])
        delta.append(delta_corn_freqs2_sta[i])
        param.append(dmp_sta[i])
        delta.append(delta_dmp_sta[i])
        number = str(i+1)
        name.append('Fc2['+number+']')
        name.append('dmp['+number+']')
    
    m2_alias = n_alias
    wi = 2. * np.arctan(1.) / m_alias
    corn_freqs2_alias = []
    dmp_alias = []
    typ2_alias = []
    for i in np.arange(1,n_alias+1,1):
        typ2_alias.append('lp2')
        corn_freqs2_alias.append(alias)
        dmp_alias.append(np.sin(wi * (2. * i - 1)))
        param.append(alias)
        param.append(np.sin(wi * (2. * i - 1)))
        delta.append(0.)
        delta.append(0.)
        name.append('F2ali')
        name.append('dali')
        
    
    m1c = m1a + len(corn_freqs1_alias)
    m2c = m2a + len(corn_freqs2_alias)
    einf0 = np.zeros(npts)
    ausf0 = np.zeros(npts)
    
    syspar_alias, m0_alias, m1_alias, m2_alias =\
            def_sys_par(syspar0, dt, 0, m1_alias, m2_alias,\
                        1., delay, sub, til,\
                        typ1_alias, typ2_alias,\
                        corn_freqs1_alias,\
                        corn_freqs2_alias, dmp_alias)
    
    sr_alias, si_alias, resid_alias, residi_alias =\
            freqDamp2paz(syspar_alias, sr0, si0, resid0,\
                         residi0, 0, m1_alias, m2_alias)
    
    einf = ltisim(1, eing.data, ausf0, einf0, 0., 0., 0.,\
                  sr_alias, si_alias, resid_alias,\
                  residi_alias, 0, m1_alias, m2_alias, dt, npts)
    
    ausf = ltisim(1, ausg.data, ausf0, einf0, 0., 0., 0.,\
                  sr_alias, si_alias, resid_alias,\
                  residi_alias, 0, m1_alias, m2_alias, dt, npts)
    print ''
    print 'Anti alias-filter of order ',m_alias,\
          ' and corner frequency ',alias,'Hz applied to data!'
    print '... writing files "' + st1[0].stats.station + '.' + st1[0].stats.channel + \
          '.f.msd" and "' + st2[0].stats.station + '.' + st2[0].stats.channel  + '.f.msd"'
    st_einf = Stream([Trace(data=einf, header=stats)])
    st_einf.write(st1[0].stats.station + '.' + st1[0].stats.channel + ".f.msd", format='MSEED')
    st_ausf = Stream([Trace(data=ausf, header=stats)])
    st_ausf.write(st2[0].stats.station + '.' + st2[0].stats.channel + ".f.msd", format='MSEED')
    
    ###########################################################
    # Start model
    m0_ges = m0_sta
    m1_ges = m1_sta + m1_alias
    m2_ges = m2_sta + m2_alias
    
    typ1_ges = []
    corn_freqs1_ges = []
    for i in np.arange(0,m1_sta,1):
        typ1_ges.append(typ1_sta[i])
        corn_freqs1_ges.append(corn_freqs1_sta[i])
    for i in np.arange(0,m1_alias,1):
        typ1_ges.append(typ1_alias[i])
        corn_freqs1_ges.append(corn_freqs1_alias[i])
    typ2_ges = []
    corn_freqs2_ges = []
    dmp_ges = []
    for i in np.arange(0,m2_sta,1):
        typ2_ges.append(typ2_sta[i])
        corn_freqs2_ges.append(corn_freqs2_sta[i])
        dmp_ges.append(dmp_sta[i])
    for i in np.arange(0,m2_alias,1):
        typ2_ges.append(typ2_alias[i])
        corn_freqs2_ges.append(corn_freqs2_alias[i])
        dmp_ges.append(dmp_alias[i])
    
    # simulate model with start parameters
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
    
    qnorm = 0.
    for i in np.arange(0,npts,1):
        qnorm = qnorm + ausf[i]**2
        qn = qnorm
    
    q = quad(qn, diff, npts)
    st_diff = Stream([Trace(data=diff, header=stats)])
    st_diff.write("diff.msd", format='MSEED')
    
    simulate = ausf - diff
    print ''
    print 'Output simulated with system start parameters '\
          'from sample ' + str(ns1) + ' to ' + str(ns2) + '!'
    print '... writing file "' + ausg.stats.station + '.' +\
                                 ausg.stats.channel + '.sim.msd"'
    st_simulate = Stream([Trace(data=simulate, header=stats)])
    st_simulate.write(ausg.stats.station + '.' + ausg.stats.channel +\
                      '.sim.msd', format='MSEED')
    print '----------------------------------------------'
    print ''
    
    ##########################################################
    # iteration with conjugate gradientes method
    noimp = 0
    step = 1.
    gnorm = 0.
    mp = len(param)
    nap = 0
    act_name = []
    corn_freqs1_fin = []
    corn_freqs2_fin = []
    dmp_fin = []
    
    for i in range(mp):
        if delta[i] > 0:
            nap = nap +1
            act_name.append(name[i])
    x = np.zeros(nap)
    print 'Iteration stops when in ' + str(nap) + ' successive steps'
    print 'RMS did not improve more than ' + str(qac) + ' and'
    print 'step is lower than ' + str(finac) + '!'
    print '   i', '   step    ', '    RMS     ', 
    for i in range(nap):
        print '%15s' % act_name[i],
    print ''
    
    for niter in range(maxit):
        qalt = q
        x, q, d, fin_diff, step, axi, gnorm,\
        amp, delay, sub, til, corn_freqs1, corn_freqs2, dmp =\
                       congrad(niter, mp, nap, x, q, qn, finac, delta, eing.data, ausf, einf,\
                               m0_ges, m1_ges, m1c, m2_ges, m2c,\
                               typ1_ges, typ2_ges, gnorm, step, dt, npts, param,\
                               syspar0, sr0, si0, resid0, residi0)
        RMS = np.sqrt(q)
        noimp = noimp + 1
        print '%(niter)4i %(step)9e %(RMS)9e' \
              % {"niter": niter, "step": axi, "RMS": RMS}, '   ',
        if 'amp' in act_name:
            print '%9e' % amp, '   ',
        if 'delay' in act_name:
            print '%9e' % delay, '   ',
        if 'sub' in act_name: 
            print '%9e' % sub, '   ',
        if 'til' in act_name:
            print '%9e' % til, '   ',
        for i in range(m1a):
            if 'Fc1['+str(i+1)+']'in act_name:
                if i == m1a - 1:
                ############################################################
                    if m2a > 0:
                        print '%9e' % corn_freqs1[i], '   ',
                    else:
                        print '%9e' % corn_freqs1[i], '   '
                else:
                    print '%9e' % corn_freqs1[i], '   ',

        for i in range(m2a):
            if 'Fc2['+str(i+1)+']'in act_name:
                print '%9e' % corn_freqs2[i], '   ',
                print '%9e' % dmp[i],'   ',
        print ''
        if np.mod(niter+1,nap) == 0:
            print ''
    
    # Stop the iteration 
        if np.sqrt(qalt) - np.sqrt(q) > qac or axi > finac:
            noimp = 0
        if noimp >= nap:
            print 'CONVERGED'
            print '-----------------------------------------------'
            print 'final system parameters:'
            print '%(niter)4i %(step)9e %(RMS)9e' \
                  % {"niter": niter, "step": axi, "RMS": RMS}, '   ',
            if 'amp' in act_name:
                print '%9e' % amp, '   ',
            if 'delay' in act_name:
                print '%9e' % delay, '   ',
            if 'sub' in act_name:
                print '%9e' % sub, '   ',
            if 'til' in act_name:
                print '%9e' % til, '   ',
            for i in range(m1a):
                if 'Fc1['+str(i+1)+']'in act_name:
                    if m2a > 0:
                        print '%9e' % corn_freqs1[i], '   ',
                    else:
                        print '%9e' % corn_freqs1[i], '   '
                corn_freqs1_fin.append(corn_freqs1[i])
            for i in range(m2a):
                if 'Fc2['+str(i+1)+']'in act_name:
                    print '%9e' % corn_freqs2[i], '   ',
                    print '%9e' % dmp[i],'   ',
                corn_freqs2_fin.append(corn_freqs2[i])
                dmp_fin.append(dmp[i])
            print ''
            print '-----------------------------------------------'
            print ''
            print '... writing file "' + ausg.stats.station + '.' +\
                                         ausg.stats.channel + '.finfit.msd"'
            fin_sim = ausf - fin_diff
            st_final = Stream([Trace(data=fin_sim, header=stats)])
            st_final.write(ausg.stats.station + '.' + ausg.stats.channel +\
                           '.finfit.msd', format='MSEED')
            print '... writing file "' + ausg.stats.station + '.' +\
                                         ausg.stats.channel + '.findiff.msd"'
            st_diff = Stream([Trace(data=fin_diff, header=stats)])
            st_diff.write(ausg.stats.station + '.' + ausg.stats.channel +\
                          '.findiff.msd', format='MSEED')
            
    # calculate poles of final system
            print '... writing file ' + ausg.stats.station + '.' + ausg.stats.channel + '.paz'
            syspar_fin, m0_fin, m1_fin, m2_fin =\
                        def_sys_par(syspar0, dt, m0_sta, m1_sta, m2_sta,\
                                    amp, delay, sub, til,\
                                    typ1_sta, typ2_sta,\
                                    corn_freqs1_fin,\
                                    corn_freqs2_fin, dmp_fin)
    
            sr_fin, si_fin, resid_fin, residi_fin =\
                        freqDamp2paz(syspar_fin, sr0, si0, resid0, residi0,\
                                     m0_fin, m1_fin, m2_fin)
    
            sr_fin = sr_fin[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
            si_fin = si_fin[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
    
            #resid_fin = resid_fin[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
            #residi_fin = residi_fin[m0_fin+1:m0_fin+1+m1_fin+2*m2_fin]
    
    # write paz file according to GSE2 standard
            paz_file_name = ausg.stats.station + '.'\
                            + ausg.stats.channel + '.paz'
            firstLine = 'CAL1 %(station)5s          %(channel)3s        PAZ\n'\
                       % {'station': ausg.stats.station, 'channel': ausg.stats.channel}
            if DataType == 'Dsp':
                nzeros = 3
            if DataType == 'Vel':
                nzeros = 2
            if DataType == 'Acc':
                nzeros = 1
    
            poles = []
            zeros = []
    
            paz_file = open(paz_file_name, 'w')
            paz_file.write(firstLine)
            paz_file.write(str(len(sr_fin))+'\n')
            for i in range(len(sr_fin)):
                paz_file.write(str(sr_fin[i]) + ' ' + str(si_fin[i]) + '\n')
                poles.append(complex(sr_fin[i], si_fin[i]))
            paz_file.write(str(nzeros)+'\n')
            for i in range(nzeros):
                paz_file.write('0.0 0.0\n')
                zeros.append(complex(0.0, 0.0))
            paz_file.write('1.0')
            paz_file.close()
            print 'finished!'
            f.close()
    
            return st_final, st_diff, poles, zeros
    # plot resulting transfer function
    #        CalcResp(poles, zeros, 1.0, MaxPer, samprate)
    #        sys.exit(1)
    
    print ''
    print 'NOT CONVERGED!'
    print ''
    print '... writing file "' + ausg.stats.station + '.' +\
                                 ausg.stats.channel + '.finfit.msd"'
    fin_sim = ausf - fin_diff
    st_final = Stream([Trace(data=fin_sim, header=stats)])
    st_final.write(ausg.stats.station + '.' + ausg.stats.channel +\
                   '.finfit.msd', format='MSEED')
    print '... writing file "' + ausg.stats.station + '.' +\
                                 ausg.stats.channel +'.findiff.msd"'
    st_diff = Stream([Trace(data=fin_diff, header=stats)])
    st_diff.write(ausg.stats.station + '.' + ausg.stats.channel +\
                  '.findiff.msd', format='MSEED')
    f.close()
    poles = []
    zeros = []
    return st_final, st_diff, poles, zeros
