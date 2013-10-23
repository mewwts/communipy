import numpy as np
import itertools as it
import numexpr as nr
from operator import itemgetter

def diagonal_modularity(diag, k, m):
    return (1/(2*m))*nr.evaluate("sum(diag)") -(1/(4*m**2))*sum(i**2 for i in k)# #(1/(4*m**2))*nr.evaluate("sum(k**2)")
    
def modularity(A, k, m, C):
    q = 0.0
    for name, c in C.get_communities().iteritems():
        rowslice = A[c,:]
        q += (1/(2*m))*np.sum(rowslice.data[np.in1d(rowslice.indices, c)]) - (C.get_community_strength(name)/(2*m))**2
    return q

def calc_modularity(row, m, n, k, C, i):
    
    c_i = C.get_community(i)

    # find the neighboring communities, exluding the community of i itself.
    coms = {}.fromkeys((C.get_community(x) for x in row.indices if C.get_community(x) != c_i)).keys()

    # If there are no neighbouring communities we exit
    if not coms:
        return None
    
    # for each of the communities, calculate the strength
    const = k[i]/(2*m**2)
    com_sum_k = (const*C.get_community_strength(x) for x in coms)
    
    # For each of the neighboring communities, find the nodes of this community attached to i.
    com_intersect_row = (np.intersect1d(C.get_nodes(x), row.indices) for x in coms)    

    # calculate the edge sum of all nodes connected to i for each community
    com_sum_a = ((1/m)*np.sum(row.data[np.in1d(row.indices, y)]) for y in com_intersect_row)
    
    # calculate the actual modularity including the gain/loss of moving i out of community c_i
    moveout = moveout_modularity(row, C, m, k, i)
    
    mods = (a - b + moveout for a,b in it.izip(com_sum_a, com_sum_k))
   
    return it.izip(coms, mods)
     
def alt_calc_modularity(row, m, n, k, C, i):
    getcom = C.get_community
    getcomstrength = C.get_community_strength

    modularities = {}
    k_i = k[i]
    const = k_i/(2*m**2)
    c_i = getcom(i)
    k_c_i = getcomstrength(c_i) - k_i 

    moveout = (2.0/(4*m**2))*k_i*k_c_i
    
    for k,j in enumerate(row.indices):
        c_j = getcom(j)
        if c_j == c_i:
            if i != j:
                moveout -= row.data[k]/m
            continue
        if c_j in modularities:
            modularities[c_j] += row.data[k]/m
        else:
            modularities[c_j] = - const*getcomstrength(c_j)  + row.data[k]/m
    
    for key in modularities:
        modularities[key] += moveout
    if not modularities:
        return -1, -1
    return max(modularities.iteritems(), key=itemgetter(1))


def moveout_modularity(row, C, m, k, i):
    com = C.get_community(i)
    com_less_i = C.get_neighbors_not_i(i)
    k_i = k[i]
    k_c = C.get_community_strength(com) - k_i 
    a = (1.0/m)*np.sum(row.data[np.in1d(row.indices, com_less_i)])
    ks = (2.0/(4*m**2))*k_i*k_c
    mod = -a + ks 
    return mod

def get_max_gain(row, m, n, k, C, i):
    """
    returns the community c and the corresponding gain in modularity of moving
    vertex i there.
    """
    return alt_calc_modularity(row, m, n, k, C, i)
    # mods =  calc_modularity(row, m, n, k, C, i)
    # try:
    #     mod = max(mods)
    #     return mod[0], mod[1]
    # except TypeError:
    #     return -1, -1
