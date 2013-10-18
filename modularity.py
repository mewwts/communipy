import numpy as np
import itertools as it
import operator as op

def modularity(A, k, m, C):
    """
    This is now ENTIRELY CORRECT YEESSSSS
    """
    q = 0.0
    for name, c in C.get_communities().iteritems():
        rowslice = A[c,:]
        q += (1/(2*m))*np.sum(rowslice.data[np.in1d(rowslice.indices, c)]) - (C.get_community_strength(name)/(2*m))**2
    return q

def movein_modularity(row, m, k, C, i):
    
    # get the unique communities present in the fastest way. (oct 7)
    getcom = C.get_community
    c_i = getcom(i)
    coms = {}.fromkeys((getcom(x) for x in row.indices if getcom(x) != c_i)).keys()
    
    # for each of the communities, calculate the strength
    const = k[i]/(2*m**2)
    #com_sum_k = (c*np.sum(k[C.get_nodes(x)]) for x in coms)
    com_sum_k = (const*C.get_community_strength(x) for x in coms)
    
    # find the nodes in each community present in this row.
    com_intersect_row = (np.intersect1d(C.get_nodes(x), row.indices) for x in coms)
    
    # calculate the edge sum of all nodes connected to i for each community
    com_sum_a = ((1/m)*np.sum(row.data[np.in1d(row.indices, y)]) for y in com_intersect_row)

    mods = it.imap(op.sub, com_sum_a, com_sum_k)
    return it.izip(mods, coms)

def moveout_modularity(row, C, m, k, i):
    #com = C.get_neighbors(i) ## PERHAPS NOT I???
    
    com_less_i = C.get_neighbors_not_i(i)
    k_i = k[i]
    k_c = np.sum(k[com_less_i])
    a = (-1.0/m)*np.sum(row.data[np.in1d(row.indices, com_less_i)])
    ks = (2.0/(4*m**2))*k_i*k_c # + np.sum(row.data[row.indices == i])/(2*m) 
    
    mod = a + ks 
    
    return mod

def get_max_gain(row, m, k, C, i):
    """
    returns the community c and the corresponding gain in modularity of moving
    vertex i there.
    """
    mods = movein_modularity(row, m, k, C, i)
    moveout = moveout_modularity(row, C, m, k, i)
    mods = [(mod[0] + moveout, mod[1]) for mod in mods]
    if mods:
        max_mod = max(mods)
        return max_mod[0], max_mod[1]
    else:
        return -1, -1

# Graveyard:
# mods = np.multiply((1/m),com_sum_a) - np.multiply((1/(2*m**2)),np.multiply(k[i],com_sum_k))
# com_intersect_row = it.imap(lambda x: np.intersect1d(C.get_nodes(x), row.indices), coms)
# com_sum_a = map(lambda y: np.sum(row.data[np.in1d(row.indices, y)]), com_intersect_row)
# coms = {}.fromkeys(map(lambda x: C.get_community(x), row.indices)).keys()
# com_sum_k = map(lambda x: np.sum(k[C.get_nodes(x)]), coms) #paralellisere? Legge i communities.py?
# com_sum_k = [np.sum(k[C.get_nodes(x)]) for x in coms]
# coms = {C.get_community(a) : np.intersect1d(C.get_neighbors(a), row.indices) for a in row.indices} # these are interscted
# com_sum_a = map(lambda y: np.sum(row[0, y].data), com_intersect_row)
# com_intersect_row = map(lambda x: x in row_dict, coms)
# com_intersect_row = [filter(lambda x: x in row_dict, C.get_nodes(y)) for y in coms]
