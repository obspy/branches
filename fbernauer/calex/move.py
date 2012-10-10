import sys, math
import numpy as np

def move(x1, q1, nap):
    x2 = np.zeros(nap)
    q2 = 0.
    for k in range(nap):
        x2[k] = x1[k]
    q2 = q1
    return x2, q2

