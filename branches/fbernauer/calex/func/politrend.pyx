import cython
import numpy as np
cimport numpy as np

# remove trend for sub and til correction                             
      
def politrend(mm, np.ndarray[np.float64_t, ndim=1] x, n):
#def politrend(mm, x, n):
    cdef Py_ssize_t i, l
    cdef double fnh, xpol
    cdef np.ndarray[np.float64_t, ndim=1] a
    #cdef np.ndarray[np.float64_t, ndim=1] imax = np.zeros(ndi,dtype=np.float64)

    ndi = 8
#    i = cython.declare(cython.int)
#    l = cython.declare(cython.int)
#    k = cython.declare(cython.int)
#    cdef int m  = min(mm,ndi-1)
#    ndi = cython.declare(cython.int)
#    ndi = 8
#    m = cython.declare(cython.int)
    m = min(mm,ndi-1)
#    fnh = cython.declare(cython.double)
    fnh = n / 2.
    end = len(x) - 1
    y = x[:end]
    c = np.zeros((m+1,m+1),dtype=np.float64)                          
    b = np.zeros(m+1,dtype=np.float64)                                
    h = np.zeros(m+2,dtype=np.float64)                                
    #imax = np.zeros(ndi,dtype=np.float64)

    for l in xrange(0,m+1,1):                                      
        for k in xrange(0,m+1,1):
            d = np.arange(1,n+1,1, dtype=np.float64)
            d = d / fnh
            d = d - 1.0
            d = d**(l+k)
            c[l, k] = c[l, k] + d.sum()
        d = np.arange(1,n+1,1, dtype=np.float64)
        d = d / fnh
        d = d - 1.0
        d = d**l
        d = d * y
        b[l] = b[l] + d.sum()
      
    a = np.linalg.solve(c,b)
      
    for i in range(0,n,1):                                        
        xpol = a[m]
        for l in range(m,0,-1):
            xpol = xpol * ((i+1) / fnh - 1.) + a[l-1]       
        x[i] = x[i] - xpol

    return x
