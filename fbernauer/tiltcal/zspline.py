import sys
import numpy as np
from trend import trend

def zspline(typ, n1, n2, n3, n4, xin, n):
#  remove z-trend with a z-spline
    fn32 = n3 - n2
    x2 = xin[n2-1]
    x3 = xin[n3-1]
    x = xin.copy()
    if n1 < 1 or n2 < n1+1 or n3 < n2+1 or n4 < n3+1 or n4 > n:
        print 'wrong parameters for zspline!'
        sys.exit(1)
    a, b = trend(typ, n1, n2, n3, n4, x[n1:], n2-n1)
    #for i in np.arange(n1, n, 1):
    #    x[i] = xa[i-n1]
    a1 = a
    b1 = b
#    print 'n1: ', n1
#    print 'n2: ', n2
#    print 'n3: ', n3
#    print 'n4: ', n4
#    print 'a1/b1:', a1, b1
    a, b = trend(typ, n1, n2, n3, n4, x[n3:], n4-n3)
    #for i in np.arange(n3, n, 1):
    #    x[i] = xa[i-n3]
    a3 = a
    b3 = b
#    print 'a3/b3:', a3, b3
    #for j in np.arange(n1,n2+1,1):
    for j in np.arange(n1-1,n2,1):
        x[j] = x[j] - (a1 + b1 * (j - n1 + 2))
    #for j in np.arange(n2+1,n3,1):
    for j in np.arange(n2,n3-1,1):
        x[j] = x[j] - (x2 + (j - n2 + 1) / fn32 * (x3 - x2))
    #for j in np.arange(n3,n4,1):
    for j in np.arange(n3-1,n4-1,1):
        x[j] = x[j] - (a3 + b3 * (j - n3 + 2))
    return x
