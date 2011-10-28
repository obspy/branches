#! /usr/bin/env python

import sys, math
import numpy as np

def gauss(c,m,n,b,a):
    ndi = 8
#    m = min(mm,ndi-1)
    fnh = n / 2.
    h = np.zeros(ndi+1)
    imax = np.zeros(ndi)

    for l in np.arange(0,m,1):
        aikmax = 0.
        for k in np.arange(0,m,1):
            h[k] = c[l][k]
            if np.abs(h[k]) > aikmax:
                aikmax = np.abs(h[k])
                index = k
        h[m+1] = b[l]
        for k in np.arange(0,m,1):
            q = c[k][index] / h[index]
            for o in np.arange(0,m,1):
                c[k][o] = c[k][o] - q * h[o]
            b[k] = b[k] - q * h[m+2]
        for k in np.arange(0,m,1):
            c[l][k] = h[k]
        b[l] = h[m+2]
        imax[l] = index
    for l in np.arange(0,m,1):
        index = imax[l]
        a[index] = b[l] / c[l][index]
mm = 3
n = 3
m = 3
c = np.array([[2.,1.,-1.],[-3.,-1.,2.],[-2.,1.,2.]])
b = np.array([8.,-11.,-3.])
a = np.array([0.,0.,0.])

print 'c',c
print 'a',a
print 'b',b

gauss(c, m, n, b, a)

print 'c',c
print 'a',a
print 'b',b
