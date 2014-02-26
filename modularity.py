import numpy as np
import numexpr as nr
from operator import itemgetter

def diagonal_modularity(diag, k, m):
    """Calculates the modularity when all vertices are in their own community"""
    return (1.0/(2*m))*nr.evaluate("sum(diag)") -(1/(4*m**2))*sum(i**2 for i in k)
    
def modularity(A, k, m, C):
    """ 
    Calculates the global modularity by summing over each community. It is very slow.
    """
    q = 0.0
    for com, c in C.get_communities().iteritems():
        rowslice = A[c,:]
        q += (1.0/(2*m))*np.sum(rowslice.data[np.in1d(rowslice.indices, c)]) - (C.get_community_strength(com)/(2*m))**2
    return q

def calc_modularity(data, indices, m, k, C, i):
    """"
    Calculates the modularity gain of moving vertex i into the community of its
    neighbors
    """
    getcom = C.get_community
    getcomstrength = C.get_community_strength
    movein = {}
    k_i = k[i]
    c_i = getcom(i)
    const = k_i/(2.0*m**2)
    moveout = (2.0/(4.0*m**2))*k_i*(getcomstrength(c_i) - k_i)
    max_movein = (-1, -1.0)
    for ind,j in enumerate(indices): 
        
        c_j = getcom(j)
        if c_j == c_i:
            if i != j:
                moveout -= data[ind]/m
            continue

        if c_j in movein:
            movein[c_j] += data[ind]/m
        else:
            movein[c_j] = data[ind]/m - const*getcomstrength(c_j)

        if movein[c_j] > max_movein[1]:
            max_movein = (c_j, movein[c_j])

    if not movein:
        return -1, -1.0

    return (max_movein[0], max_movein[1] + moveout)

def noloops_calc_modularity(data, indices, m, k, C, i):
    """
    Calculates the modularity not allowing loops in the null model
    """
    getcom = C.get_community
    getcomstrength = C.get_community_strength
    movein = {}
    k_i = k[i]
    c_i = getcom(i)

    moveout = k_i*(getcomstrength(c_i) - k_i)/(m*(2*m - getcomstrength(c_i)))

    for ind, j in enumerate(indices):
        c_j = getcom(j)

        if c_j == c_i:
            if i != j:
                moveout -= data[ind]/m

        if c_j in movein:
            movein[c_j] += data[ind]/m
        else:
            k_c = getcomstrength(c_j)
            movein[c_j] = (data[ind]/m - 
                           ((k_i*k_c) * (k_c/(2*m-k_c) + 
                           k_i/(2*m-k_i) + 2))/(2*m*(2*m-k_c-k_i)))

    if not movein:
        return -1, -1.0
    
    return max(((i[0], i[1]+moveout) for i in movein.iteritems()), key=itemgetter(1))
