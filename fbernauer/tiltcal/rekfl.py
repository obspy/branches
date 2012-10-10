###########################################
# This function performs recursive        #
# filtering with the filter coefficientes #
# f0, f1, f2, g1, g2.                     #
###########################################


import numpy as np

def rekfl(x, n, f0, f1, f2, g1, g2):
    y = np.zeros(len(x))
    xa = 0.0
    xaa = 0.0
    ya = 0.0
    yaa = 0.0

    for i in range(n):
        xn = float(x[i])
        yn = f0 * xn + f1 * xa + f2 * xaa + g1 * ya + g2 * yaa
        y[i] = float(yn)
        xaa = xa
        xa = xn
        yaa = ya
        ya = yn

    return y
