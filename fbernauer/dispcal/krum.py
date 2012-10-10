import sys
import numpy as np


def krum(x, n, ng, xk):
    nh = (ng - 1) / 2
#    import ipdb; ipdb.set_trace()
    if ng < 3 or ng != 2 * nh + 1:
        print "ng ist keine ungerade Zahl >=3"
        sys.exit()
    # Konstanten
    sj = ng * (ng + 1) / 2.
    sjq = ng * (ng + 1) * (2 * ng + 1) / 6.
    # Erster Punkt des Krummheitsmasses
    #sx = sum(x[0:ng+1])
    sx = 0.0
    sjx = 0.0
    for j in range(ng):
        sx = sx + x[j]
        sjx = sjx + (j + 1) * x[j]
    det = ng * sjq - sj ** 2
    a = (sx * sjq - sjx * sj) / det
    b = (ng * sjx - sj * sx) / det
    var = 0.0
    for j in range(ng):
        var = var + (x[j] - a - (j + 1) * b) ** 2
    xk[0] = np.sqrt(var / ng)
    for j in np.arange(1,nh + 1,1):
        xk[j] = xk[0]

    # Weitere Punkte rekursiv
    for k in np.arange(nh+1, n-nh, 1):
        sjx = sjx - sx + ng * x[nh + k]
        sx = sx - x[k - nh - 1] + x[k + nh]
        a = (sx * sjq - sjx * sj) / det
        b = (ng * sjx - sj * sx) / det
        var = 0.0
        for j in np.arange(k-nh-1, k+nh, 1):
            var = var + (x[j] - a - ((j + 1) - (k + 1) + nh + 1) * b) ** 2

        xk[k] = np.sqrt(var / ng)
    for k in np.arange(n-nh-1, n, 1):
        xk[k] = xk[n - nh - 1]

    np.savetxt('xk_test', xk)
    return xk
