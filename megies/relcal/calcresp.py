# calculate transfer function of known system
#
# input parameters:
# calfile: file containing poles, zeros and scale factor 
#          for known system

import sys
import numpy as np

def calcresp(calfile, nfft, sampfreq):
    buffer = np.empty(nfft/2+1, dtype='complex128')
    poles = []
    zeros = []
    file = open(str(calfile), 'r')

    # read file until calibration section is found
    print '...reading calibration file'
    text = ' '
    while text != 'CAL1':
        textln = file.readline()
        text = textln.split(' ')[0]
    if not text == 'CAL1':
        msg = 'could not find calibration section!'
        raise NameError(msg)
    else:
        cal = textln[31:34]
    if cal == 'PAZ':
        # read poles
        npoles = int(file.readline())
        for i in xrange(npoles):
            pole = file.readline()
            pole_r = float(pole.split(" ")[0])
            pole_i = float(pole.split(" ")[1])
            pole_c = pole_r + pole_i * 1.j
            poles.append(pole_c)
        # read zeros
        nzeros = int(file.readline())
        for i in xrange(nzeros):
            zero = file.readline()
            zero_r = float(zero.split(" ")[0])
            zero_i = float(zero.split(" ")[1])
            zero_c = zero_r + zero_i * 1.j
            zeros.append(zero_c)
        # read scale factor
        scale_fac = float(file.readline())
        file.close
    
        # calculate transfer function
        delta_f = sampfreq / nfft
        F = np.empty(nfft/2+1)
        for i in xrange(nfft/2 + 1):
            fr = i * delta_f
            F[i] = fr
            om = 2 * np.pi * fr
            num = 1. + 0.j
            
            for ii in xrange(nzeros):
                s = 0. + om * 1.j
                dif = s - zeros[ii]
                num = dif * num
    
            denom = 1. + 0.j
            for ii in xrange(npoles):
                s = 0. + om * 1.j
                dif = s - poles[ii]
                denom = dif * denom
    
            t_om = 1. + 0.j
            if denom.real != 0. or denom.imag != 0.:
                t_om = num / denom
            
            t_om *= scale_fac
           
            if i < nfft/2 and i > 0:
                buffer[i] = t_om
    
            if i == 0:
                buffer[i] = t_om + 0.j
        
            if i == nfft/2:
                buffer[i] = t_om + 0.j
        
        return buffer, F

    else:
        msg = '%s type not known!'%(cal)
        raise NameError(msg)
