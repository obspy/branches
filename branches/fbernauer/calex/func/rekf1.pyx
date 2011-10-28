import sys, math
import numpy as np
cimport numpy as np

# Rekursive Filters:
# ein: Array with input data
# sum: Array with output data

def rekf1(double dt, double r, int n,\
          np.ndarray[np.float64_t, ndim=1] ein,\
          np.ndarray[np.float64_t, ndim=1] sum):
    cdef Py_ssize_t i
    cdef double z = np.exp(dt)
    cdef double aus0 = r * ein[0]
    sum[0] = sum[0] + aus0
    for i in np.arange(1,n,1):
        aus0 = r * ein[i] + z * aus0
        sum[i] = sum[i] + aus0
    
    return sum
