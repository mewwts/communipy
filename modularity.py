import numpy as np
#import itertools as it
import numexpr as nr
from operator import itemgetter

def diagonal_modularity(diag, k, m):
    return (1.0/(2*m))*nr.evaluate("sum(diag)") -(1/(4*m**2))*sum(i**2 for i in k)# #(1/(4*m**2))*nr.evaluate("sum(k**2)")
    
def modularity(A, k, m, C):
    q = 0.0
    for name, c in C.get_communities().iteritems():
        rowslice = A[c,:]
        q += (1.0/(2*m))*np.sum(rowslice.data[np.in1d(rowslice.indices, c)]) - (C.get_community_strength(name)/(2*m))**2
    return q

def calc_modularity(data, indices, m, k, C, i):
    getcom = C.get_community
    getcomstrength = C.get_community_strength

    modularities = {}
    k_i = k[i]
    c_i = getcom(i)
    const = k_i/(2.0*m**2)    
    moveout = (2.0/(4.0*m**2))*k_i*(getcomstrength(c_i) - k_i)
    
    for l,j in enumerate(indices): 
        
        c_j = getcom(j)
        if c_j == c_i:
            if i != j:
                moveout -= data[l]/m
            continue

        if c_j in modularities:
            modularities[c_j] += data[l]/m
        else:
            modularities[c_j] = - const*getcomstrength(c_j)  + data[l]/m
    
    if not modularities:
        return -1, -1.0
    
    return max(((i[0], i[1] + moveout) for i in modularities.iteritems()), key=itemgetter(1))
