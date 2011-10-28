import sys, math
import numpy as np
cimport numpy as np

def quad(qn, np.ndarray[np.float64_t, ndim=1] sum, int npts):
    cdef Py_ssize_t i 
    cdef double qua
    qua = 0.
    for i in xrange(0,npts,1):
        qua = qua + sum[i]**2
    return qua / qn

