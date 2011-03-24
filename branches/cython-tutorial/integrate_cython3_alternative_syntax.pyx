import cython

cdef double f(double x):
    return x**2-x

@cython.locals(a=cython.double, b=cython.double, N=cython.int)
def integrate(a, b, N):
    i = cython.declare(cython.int)
    s = cython.declare(cython.double)
    dx = cython.declare(cython.double)
    s = 0
    dx = (b-a)/N
    for i in range(N):
        s += f(a+i*dx)
    return s * dx
