def trend(typ, n1, n2, n3, n4, x, n):
#  remove trend
#    import ipdb; ipdb.set_trace()
    if typ == 'tre':
        if n2 <= 1 or n2 > n:
            n2 = n
        gn = n2
        alpha = 0.5 * gn * (gn + 1.0)
        beta = (2.0 * gn + 1.0) * (gn + 1.0) * gn / 6.0
        det = gn * beta - alpha * alpha
        sx = 0.0
        sjx = 0.0
        for j in range(n2):
            sx = sx + x[j]
            sjx = sjx + (j + 1) * x[j]
        a = (sx * beta - sjx * alpha) / det
        b = (sjx * gn - sx * alpha) / det
    elif typ == 'zsp':
        n2 = n
        gn = n
        alpha = 0.5 * gn * (gn + 1.0)
        beta = (2.0 * gn + 1.0) * (gn + 1.0) * gn / 6.0
        det = gn * beta - alpha * alpha
        sx = 0.0
        sjx = 0.0
        for j in range(n2):
            sx = sx + x[j]
            sjx = sjx + (j + 1) * x[j]
        a = (sx * beta - sjx * alpha) / det
        b = (sjx * gn - sx * alpha) / det
        return a, b
    else:
        b = x[n] - x[1] / float(n-1)
        a = x[1] - b
    for j in range(n2):
        x[j] = x[j] - (a + b * (j + 1))
        return x
      
