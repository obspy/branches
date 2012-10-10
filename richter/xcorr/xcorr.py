#!/usr/bin/python

import numpy as np
import obspy.signal
from _xcorr import xcorr as xcorr_c

def xcorr_obspy(tr1, tr2, shift_len, shift2 = 0, pad=1):
    N1 = abs(len(tr1)-len(tr2))//2
    N2 = (abs(len(tr1)-len(tr2))+1)//2
    if pad in (1,2):
        if len(tr1) > len(tr2):
            tr2 = np.hstack((np.zeros(N1), tr2, np.zeros(N2)))
        elif len(tr1) < len(tr2):
            tr1 = np.hstack((np.zeros(N1), tr1, np.zeros(N2)))
        N = len(tr1)
        if pad != 0 and N < 4*shift_len:
            zeros = np.zeros((4*shift_len-N)//2)
            tr1 = np.hstack((zeros, tr1, zeros))
            tr2 = np.hstack((zeros, tr2, zeros))
        if shift2 != 0:
            zeros = np.zeros(shift2)
            tr1 = np.hstack((tr1, zeros))
            tr2 = np.hstack((zeros, tr2))
    if pad ==3 and len(tr1) != len(tr2):
        if len(tr1)<len(tr2):
            if len(tr1) < 4*shift_len:
                zeros = np.zeros((4*shift_len-len(tr1))//2)
                tr1 = np.hstack((zeros, tr1, zeros))
            if len(tr2) > 4*shift_len:
                tr2 = tr2[:4*shift_len]
    return obspy.signal.xcorr(tr1, tr2, shift_len, full_xcorr=True)[2]

def xcorr(tr1, tr2, shift_len, shift_zero=0, padding=1, twosided=True, demean=True):
    """
    Cross-correlation of numpy arrays tr1 and tr2.

    The data is demeaned before cross-correlation and zero-padded as
    required. But this is done after demeaning. Because zero-padding has an
    effect on demeaning you can do it explecitely beforhand with the parameter
    padding. After cross-correlation the result is normalized.

    tr1, tr2: data
    shift_len: samples to shift
    shift_zero: shift tr1 before cross-correlation this amount of samples to the right
                (this means correlation function is shifted to the right
                 or better: the window of what you get of the function
                 is shifted to the left)
                do not use in combination with twosided = False
    padding: 0 no zero padding
             >0 zero padding on both sides of both arrays to the length of
             1  max(len(tr1), len(tr2))
             2  max(len(tr1), len(tr2)) + shift_len
             >2 max(len(tr1), len(tr2)) + padding
    twosided: if False only the right/positive side is returned. This can be
              usefull for auto-correlation. By the way you will get the same
              result with adapted parameters shift_len and shift_zero.
    demean: demean data beforehand
    return:
        numpy array with correlation function of length (twosided+1)*shift_len+1
    """
    if padding:
        N1 = len(tr1)
        N2 = len(tr2)
        maxN=max(N1,N2)
        if padding ==1:
            z1 = np.zeros((maxN-N1)//2)
            z2 = np.zeros((maxN-N2)//2)
        elif padding==2:
            z1 = np.zeros((maxN-N1)//2+shift_len)
            z2 = np.zeros((maxN-N2)//2+shift_len)
        else:
            z1 = np.zeros((maxN-N1)//2+padding)
            z2 = np.zeros((maxN-N2)//2+padding)
        tr1 = np.hstack((z1, tr1, z1))
        tr2 = np.hstack((z2, tr2, z2))
    return xcorr_c(tr1, tr2, shift_len, shift_zero, bool(twosided), bool(demean))

def acorr(tr, shift_len,  shift_zero=0, padding=1, twosided=False, demean=True):
    """
    Auto-correlation of array tr.

    It calls xcorr with parameter twosided=False.
    See doc for xcorr for further information.
    """
    res = xcorr(tr, tr, shift_len,  shift_zero = shift_zero, padding=padding, twosided=False, demean=demean)
    if twosided:
        res = np.hstack((res[::-1], res[1:]))
    return res