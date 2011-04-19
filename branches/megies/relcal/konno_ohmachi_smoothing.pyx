# -*- coding: utf-8 -*-
#-------------------------------------------------------------------
# Filename: konno_ohmachi_smoothing.py
#  Purpose: Small module to smooth spectra with the so called Konno & Ohmachi
#           method.
#   Author: Lion Krischer
#    Email: krischer@geophysik.uni-muenchen.de
#  License: GPLv2
#
# Copyright (C) 2010 Lion Krischer
#---------------------------------------------------------------------

import numpy as np
cimport numpy as np

# Define the maximum memory the smoothing is allowed to use for the smoothing
# matrix. This corresponds to a length of a single spectrum of about 16000.
# Larger spectrum arrays will be calculated frequency by frequency and the
# smoothing window will be deleted in between. This takes a long time when
# smoothing several spectra but reduces memory usage.
# MAX_MEMORY_IN_MB = 1024


def konno_ohmachi_smoothing_window(np.ndarray[np.float32_t, ndim=1] frequencies, float center_frequency, double bandwidth):
#def konno_ohmachi_smoothing_window(frequencies, center_frequency, double bandwidth):
    """
    Returns the Konno & Ohmachi Smoothing window.

    The following commentary is from Geopsy:
    /*!
    Smoothing with the "Konno-Ohmachi" function

    W(f) = (sin(bexp*log10(f/fc)) / (bexp*log10(f/fc)))^4,

    where fc is the frequency around which the smoothing is performed.
    \a bexp determines the exponent 10^(2.5/exp) which is the half-width of
    the peak.
    */

    Returns the smoothing window around the center frequency with one value per
    input frequency.

    :param frequencies: All frequencies for which the smoothing window will be
        returned.
    :type frequencies: numpy.ndarray
    :param center_frequency: The frequency around which the smoothing is
        performed.
    :param bandwidth: Determines the width of the smoothing peak. Lower values
        result in a broader peak.
    """
    
    cdef np.ndarray[np.float32_t, ndim=1] smoothing_window

    # If the center_frequency is 0 return an array with zero everywhere except
    # a one at the first sample.
    if center_frequency == 0:
        smoothing_window = np.zeros(len(frequencies),'float32')
        smoothing_window[0] = 1
        smoothing_window /= smoothing_window.sum()
        return smoothing_window
    # Just the Konno-Ohmachi formulae.
    smoothing_window = (np.sin(bandwidth * np.log10(frequencies / \
           center_frequency)) / (bandwidth * np.log10(frequencies / \
           center_frequency))) ** 4
    # Remove NaN values.
    smoothing_window[np.isnan(smoothing_window)] = 0
    # Normalize to one.
    smoothing_window /= smoothing_window.sum()
    return smoothing_window


def calculate_smoothing_matrix(np.ndarray[np.float32_t, ndim=1] frequencies, double bandwidth):
#def calculate_smoothing_matrix(frequencies, double bandwidth):
    """
    Calculates a len(frequencies) x len(frequencies) matrix with the Konno &
    Ohmachi window for each frequency as the center frequency.

    Any spectrum with the same frequency bins as this matrix can later be
    smoothed by a simple matrix multiplication with this matrix:
        smoothed_spectrum = np.dot(spectrum, smoothing_matrix)

    This also works for many spectra stored in one large matrix and is even
    more efficient.

    This makes it very efficient for smoothing the same spectra again and again
    but it comes with a high memory consumption for larger frequenciy arrays!

    :param frequencies: The input frequencies.
    :param bandwidth: The bandwidth for the Konno & Ohmachi window.
    """
    #cdef np.ndarray[np.float32_t, ndim=1] nfrequencies
    cdef Py_ssize_t _i
    cdef float freq
    cdef np.ndarray[np.float32_t, ndim=2] sm_matrix
    # Create matrix to be filled with smoothing entries. Use 32bit for reduced
    # memory consumption.
    sm_matrix = np.empty((len(frequencies), len(frequencies)), 'float32')
    #nfrequencies = np.require(frequencies, 'float32')
    #nfrequencies = frequencies.astype(np.float32)
    for _i, freq in enumerate(frequencies):
        sm_matrix[:,_i] = konno_ohmachi_smoothing_window(frequencies, freq,
                                                          bandwidth)
    return sm_matrix


#def smooth_spectra(spectra, np.ndarray[np.float64_t, ndim=1] frequencies, \
#                    double bandwidth, int count=1, int max_memory_in_mb=1024):
def smooth_spectra(np.ndarray[np.float64_t, ndim=1] ospectra, np.ndarray[np.float64_t, ndim=1] frequencies, \
                    double bandwidth, int count=1, int max_memory_in_mb=1024):
    """
    Smoothes a matrix containing one spectra per row with the Konno-Ohmachi
    smoothing window.

    All spectra need to have frequency bins corresponding to the same
    frequencies.

    This method first will estimate the memory usage and then either use a fast
    and memory intensive method or a slow one with a better memory usage. The
    variable MAX_MEMORY_IN_MB determines the threshold.

    :param spectra: numpy.ndarray with one spectrum per row. The spectra will
        be changed. Thus this method operates in place to reduce the memory
        consumption.
    :param frequencies: numpy.ndarray which contains the frequencies for the
        spectra.
    :param bandwidth: Controls the width of the Konno-Ohmachi smoothing window.
        A higher value mean a narrower peak. 100 seems to be a good value
        though this depends on the length of the spectra.
    :param count: How often the apply the filter. For very noisy spectra it is
        useful to apply is more than once.
    """

    cdef np.ndarray[np.float32_t, ndim=1] window, spectra, nfrequencies
    cdef np.ndarray[np.float32_t, ndim=2] new_spectra, sm_matrix
    cdef np.ndarray[np.float32_t, ndim=1] new_spec
    cdef Py_ssize_t _j, _k, _i
    cdef int rows, approx_mem_usage 
    #nd = np.shape(spectra)
    nfrequencies = frequencies.astype(np.float32)
    spectra = ospectra.astype(np.float32)
    # Calculate the approximate memory needs for the smoothing matrix using
    # float32.
    length = len(nfrequencies)
    approx_mem_usage = (length ** 2 * 4) / float(1000000)
    # If smaller than the allowed maximum memory consumption build a smoothing
    # matrix and apply to each spectrum. Also only use when more then one
    # spectrum is there.
    if approx_mem_usage <= max_memory_in_mb:
        sm_matrix = calculate_smoothing_matrix(nfrequencies, bandwidth)
        # Eventually apply more than once.
        for _i in xrange(count):
            new_spectra = np.dot(spectra, sm_matrix)
        return new_spectra
    else:
        #frequencies = frequencies.astype(np.float32)
        #frequencies = np.require(frequencies, 'float32')
        new_spec = np.empty(np.shape(spectra), 'float32')
        if len(np.shape(new_spec)) == 1:
            rows = 1
        else:
            rows = np.shape(new_spec)[0]
        for _j in xrange(rows):
            for _k in xrange(count):
                for _i in xrange(length):
                    print 'calculating smoothing window for centre frequency %f \
                            [%.1f-%.1f Hz]'%(nfrequencies[_i],np.min(nfrequencies),\
                            np.max(nfrequencies))
                    window = konno_ohmachi_smoothing_window(nfrequencies,
                                    nfrequencies[_i], bandwidth)
                    if rows == 1:
                        new_spec[_i] = (window * spectra).sum()
#                    else:
#                        new_spec[_j][_i] = (window * spectra[_j]).sum()
        return new_spec
