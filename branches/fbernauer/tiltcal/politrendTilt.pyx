import cython
import numpy as np
cimport numpy as np

# remove trend for sub and til correction                             
      
def politrendTilt(mm, np.ndarray[np.float64_t, ndim=1] x, n, np.ndarray[np.float64_t, ndim=1] z):
#def politrend(mm, x, n):
    cdef Py_ssize_t i, l
    cdef double fnh, xpol
    cdef np.ndarray[np.float64_t, ndim=1] a

    ndi = 8
    m = min(mm,ndi-1)
    fnh = n / 2.
    end = len(x) - 1
    y = x.copy()
    c = np.zeros((m+1,m+1),dtype=np.float64)                          
    b = np.zeros(m+1,dtype=np.float64)                                
    h = np.zeros(m+2,dtype=np.float64)                                

    for l in xrange(0,m+1,1):                                      
        for k in xrange(0,m+1,1):
            for i in range(n):
                if z[i] > 0.5:    
                    c[l, k] = c[l, k] + ((i + 1) / fnh - 1.0)**(l + k)
        for i in range(n):
            if z[i] > 0.5:
                b[l] = b[l] + ((i + 1) / fnh -1)**(l) * y[i]
      
    a = np.linalg.solve(c,b)
      
    for i in range(0,n,1):                                        
        xpol = a[m]
        for l in range(m,0,-1):
            xpol = xpol * ((i+1) / fnh - 1.) + a[l-1]       
        x[i] = x[i] - xpol

    return x, a
