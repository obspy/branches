import sys, math, cython
import numpy as np
from politrend import politrend
from politrend_c import politrend

mm = 3
x = np.arange(50000, dtype='float64')
n = len(x) - 1 

politrend(mm, x, n)

