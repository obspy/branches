from rekfl import rekfl

def integrate(x, n, dt):
    f0 = 1.0 / 2.0 * dt
    f1 = f0
    f2 = 0.0
    g1 = 1.0
    g2 = 0.0
    x_int = rekfl(x, n, f0, f1, f2, g1, g2)
    return x_int
