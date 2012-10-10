import numpy as np

def step(x, n1, n2, n3, n4, n):
    av1 = np.sum(x[n1:n2-1]) / (n2 - n1)
    av2 = np.sum(x[n3:n4-1]) / (n4 - n3)
    avs = av2 - av1
    return avs
