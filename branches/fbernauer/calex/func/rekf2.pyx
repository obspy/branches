import numpy as np
cimport numpy as np

def rekf2(sre, sim, rre, rim, n, np.ndarray[np.float64_t, ndim=1] ein, np.ndarray[np.float64_t, ndim=1] sum):
    cdef Py_ssize_t i
    cdef double aus0, aus1, aus2
    cdef double f0, f1, g1, g2

    zabs = np.exp(sre)
    zre = zabs * np.cos(sim)
    zim = zabs * np.sin(sim)
    f0 = 2. * rre
    f1 = -2. * (rre * zre + rim * zim)
    g1 = 2. * zre
    g2 = -zabs**2
    aus0 = f0 * ein[0]
    sum[0] = sum[0] + aus0
    aus1 = aus0
    aus0 = f0 * ein[1] + f1 * ein[0] + g1 * aus1
    sum[1] = sum[1] + aus0
    
    for i in np.arange(2,n,1):
        aus2 = aus1
        aus1 = aus0
        aus0 = f0 * ein[i] + f1 * ein[i-1] + g1 * aus1 + g2 * aus2
        sum[i] = sum[i] + aus0

    return sum
