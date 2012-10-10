############################################
# in this class functions are defined that #
# determine the filter coefficientes f0,   #
# f1, f2, g1 and g2 for rekfl.py           #
############################################

# to do: von fc, fcs auf t0, t0s: t = 1/f
#        h?

import numpy as np

#class filter(self):
#    """
#    The methods contained in this class calculate
#    the filter coeficientes f0, f1, f2, g1 and g2
#    using the corner period t0 [Hz] and the 
#    damping coeficient h.
#    The following filters are implemented:
#
#    lp1 / hp1: first order low- / high pass
#               only t0 has to be specified
#    lp2 / hp2 / bp2: second order low- / high- /
#                     band pass; t0 and h have to be 
#                     specified.
#    le1 / he1 / le2 / he2 are the corresponding
#    inverse filters.
#    """
#    def __init__(self):


def lp1(t0):
        eps = 2.0 * np.pi / t0
        f2 = 0.0
        g2 = 0.0
        g1 = (2.0 - eps) / (2.0 + eps)
        f0 = eps / (2.0 + eps)
        f1 = f0
        return f0, f1, f2, g1, g2


def lp2(t0, h):
        eps = 2.0 * np.pi / t0
        epsq = eps * eps
        a = 1.0 - eps * h + epsq / 4.0
        b = -2.0 + epsq / 2.0
        c = 1.0 + eps * h + epsq / 4.0
        g1 = - b / c
        g2 = - a / c
        f0 = epsq / 4.0 / c
        f1 = f0 + f0
        f2 = f0
        return f0, f1, f2, g1, g2
        

def hp1(t0):
        eps = 2.0 * np.pi / t0
        f2 = 0.0
        g2 = 0.0
        g1 = (2.0 - eps) / (2.0 + eps)
        f0 = 2.0 / (2.0 + eps)
        f1 = -f0
        return f0, f1, f2, g1, g2


def hp2(t0, h):
        eps = 2.0 * np.pi / t0
        epsq = eps * eps
        a = 1.0 - eps * h + epsq / 4.0
        b = -2.0 + epsq / 2.0
        c = 1.0 + eps * h + epsq / 4.0
        g1 = - b / c
        g2 = - a / c
        f0 = 1.0 / c
        f1 = - f0 - f0
        f2 = f0
        return f0, f1, f2, g1, g2

def bp2(t0, h):
        eps = 2.0 * np.pi / t0
        epsq = eps * eps
        a = 1.0 - eps * h + epsq / 4.0
        b = -2.0 + epsq / 2.0
        c = 1.0 + eps * h + epsq / 4.0
        g1 = - b / c
        g2 = - a / c
        f0 = eps / 2.0 / c
        f1 = 0.0
        f2 = -f0
        return f0, f1, f2, g1, g2


    # inverse filters
def le1(t0, t0s):
        eps = 2.0 * np.pi / t0
        epss = 2.0 * np.pi / t0s
        fac = t0s / t0
        f2 = 0.0
        g1 = (2.0 - eps) / (2.0 + eps)
        g2 = 0.0
        f0 = (epss + 2.0) / (eps + 2.0)
        f0 = f0 * fac
        f1 = (epss - 2.0) / (eps + 2.0)
        f1 = f1 * fac
        return f0, f1, f2, g1, g2
        
def he1(t0, t0s):
        eps = 2.0 * np.pi / t0
        epss = 2.0 * np.pi / t0s
        f2 = 0.0
        g1 = (2.0 - eps) / (2.0 + eps)
        g2 = 0.0
        f0 = (epss + 2.0) / (eps + 2.0)
        f1 = (epss - 2.0) / (eps + 2.0)
        return f0, f1, f2, g1, g2

def le2(t0, t0s, h, hs):
        eps = 2.0 * np.pi / t0
        epsq = eps * eps
        epss = 2.0 * np.pi / t0s
        epssq = epss * epss
        fac = (t0s / t0) ** 2
        a = 1.0 - eps * h + epsq / 4.0
        b = -2.0 + epsq / 2.0
        c = 1.0 + eps * h + epsq / 4.0
        As = 1.0 - epss * hs + epssq / 4.0
        Bs = -2.0 + epssq / 2.0
        Cs = 1.0 + epss * hs + epssq / 4.0
        g1 = - b / c
        g2 = - a / c
        f0 = (Cs / c) * fac
        f1 = (Bs / c) * fac
        f2 = (As / c) * fac
        return f0, f1, f2, g1, g2

def he2(t0, t0s, h, hs):
        eps = 2.0 * np.pi / t0
        epsq = eps * eps
        epss = 2.0 * np.pi / t0s
        epssq = epss * epss
        a = 1.0 - eps * h + epsq / 4.0
        b = -2.0 + epsq / 2.0
        c = 1.0 + eps * h + epsq / 4.0
        As = 1.0 - epss * hs + epssq / 4.0
        Bs = -2.0 + epssq / 2.0
        Cs = 1.0 + epss * hs + epssq / 4.0
        g1 = - b / c
        g2 = - a / c
        f0 = Cs / c
        f1 = Bs / c
        f2 = As / c
#        import ipdb; ipdb.set_trace()
        return f0, f1, f2, g1, g2
