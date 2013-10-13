import numpy as np
import itertools as it
import operator as op

def initial_modularity(A, k, m):
    ks = np.sum(k**2)/(2*m)
    As = np.sum(A.diagonal())
    return (As - ks)/(2*m)


def movein_modularity(row, m, k, C, i):

    # get the unique communities present in the fastest way. (oct 7)
    #coms = {}.fromkeys(map(lambda x: C.get_community(x), row.indices)).keys()
    coms = {}.fromkeys((C.get_community(x) for x in row.indices)).keys()
    # for each of the communities, calculate the strength
    #com_sum_k = map(lambda x: np.sum(k[C.get_nodes(x)]), coms) #paralellisere? Legge i communities.py?
    c = k[i]/(2*m**2)
    com_sum_k = (c*np.sum(k[C.get_nodes(x)]) for x in coms)


    
    
    # find the nodes in each community present in this row.
    #com_intersect_row = it.imap(lambda x: np.intersect1d(C.get_nodes(x), row.indices), coms)
    com_intersect_row = (np.intersect1d(C.get_nodes(x), row.indices) for x in coms)
    # calculate the edge sum of all nodes connected to i for each community
    #com_sum_a = map(lambda y: np.sum(row.data[np.in1d(row.indices, y)]), com_intersect_row)
    
    com_sum_a = ((1/m)*np.sum(row.data[np.in1d(row.indices, y)]) for y in com_intersect_row)

    mods = it.imap(op.sub, com_sum_a, com_sum_k)
    #mods = np.multiply((1/m),com_sum_a) - np.multiply((1/(2*m**2)),np.multiply(k[i],com_sum_k))

    return it.izip(mods, coms)

def moveout_modularity(row, C, m, k, i):
    com = C.get_neighbors(i)
    if len(com) > 1:
        mod = (-1/m)*np.sum(row.data[np.in1d(row.indices, com)]) + (1/(2*m**2))*k[i]*np.sum(k[com]) - (k[i]**2)/(2*m**2) 
    else:
        mod = - (k[i]**2)/(2*m**2) 
    return mod


def get_max_gain(row, m, k, C, i):
    """
    returns the community c and the corresponding gain in modularity of moving
    vertex i there.
    """
    mods = movein_modularity(row, m, k, C, i)
    moveout = moveout_modularity(row, C, m, k, i)
    c_i = C.get_community(i)
    mods = [(mod[0] + moveout, mod[1]) for mod in mods if mod[1] != c_i]

    if mods:
        max_mod = max(mods)
        return max_mod[0], max_mod[1]
    else:
        return -1, -1

# Graveyard:
#com_sum_k = [np.sum(k[C.get_nodes(x)]) for x in coms]
# coms = {C.get_community(a) : np.intersect1d(C.get_neighbors(a), row.indices) for a in row.indices} # these are interscted
# com_sum_a = map(lambda y: np.sum(row[0, y].data), com_intersect_row)
# com_intersect_row = map(lambda x: x in row_dict, coms)
# com_intersect_row = [filter(lambda x: x in row_dict, C.get_nodes(y)) for y in coms]
