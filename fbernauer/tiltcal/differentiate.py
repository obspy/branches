import numpy as np

def differentiate(x, n, dt, s):
# calculate derivative (non-recursive, non-causal, symmetric-difference)
    twodt = 2.0 * dt
    x_diff = np.zeros(n)
    for j in range(n-2):
        x_diff[j] = (x[j+2] - x[j]) / twodt
    x_diff[n-2] = x[n-2]
    x_diff[n-1] = x[n-1]
    for j in np.arange(n-2, 1, -1):
        x_diff[j] = x_diff[j-1]
    x_diff[n-1] = x_diff[n-2]
    
    if s == 1:
        print ''
        print 'computed derivative by symmetric differences...'
        print ''

    return x_diff
