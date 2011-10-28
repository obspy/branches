import sys
import numpy as np
from trend import trend

def mspline(typ, n1, n2, n3, n4, xin, n):
#  remove trend with a m-spline
    fn32 = n3 - n2
    x2 = xin[n2-1]
    x3 = xin[n3-1]
    x = xin.copy()
    if n1 < 1 or n2 < n1+1 or n3 < n2+1 or n4 < n3+1 or n4 > n:
        print 'wrong parameters for zspline!'
        sys.exit(1)
    a, b = trend(typ, n1, n2, n3, n4, x[n1:], n2-n1)
    a1 = a
    b1 = b
    a, b = trend(typ, n1, n2, n3, n4, x[n3:], n4-n3)
    a3 = a
    b3 = b
    for j in np.arange(n1-1,n4,1):
        x[j] = x[j] - (a1 + b1 * (j - n1 + 2)) / 2.0
    for j in np.arange(n1-1,n4-1,1):
        x[j] = x[j] - (a3 + b3 * (j - n3 + 2)) / 2.0
    return x
