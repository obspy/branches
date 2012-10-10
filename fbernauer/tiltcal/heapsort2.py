import numpy as np

def heapsort(n, ra):
#    import ipdb; ipdb.set_trace()
    l = n / 2 + 1
    ir = n

    while l > 1:
        l = l - 1
        rra = ra[l-1]

    	i = l
    	j = l + l
    	while j <= ir:
            if j < ir:
    	        if ra[j-1] < ra[j]:
                    j=j+1
            if rra < ra[j-1]:
    	        ra[i-1] = ra[j-1]
    	        i = j
    	        j = j + j
    	    else:
        	    j = ir + 1
        ra[i-1] = rra

    while l <= 1:
        rra = ra[ir-1]
        ra[ir-1] = ra[0]
        ir = ir - 1
        if ir == 0:
            ra[0] = rra
            return ra

    	i = l
    	j = l + l
    	while j <= ir:
            if j < ir:
    	        if ra[j-1] < ra[j]:
                    j=j+1
            if rra < ra[j-1]:
    	        ra[i-1] = ra[j-1]
    	        i = j
    	        j = j + j
    	    else:
        	    j = ir + 1
        ra[i-1] = rra
