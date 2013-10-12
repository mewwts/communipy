import numpy as np

def initial_modularity(A, k, m):
    ks = np.sum(k**2)/(2*m)
    As = np.sum(A.diagonal())
    return (As - ks)/(2*m)


def movein_modularity(row, m, k, C, i):

    # get the unique communities present in the fastest way. (oct 7)
    coms = {}.fromkeys(map(lambda x: C.get_community(x), row.indices)).keys()
    # for each of the communities, calculate the strength
    com_sum_k = map(lambda x: np.sum(k[C.get_nodes(x)]), coms) #paralellisere? Legge i communities.py?
    # find the nodes in each community present in this row.
    com_intersect_row = map(lambda x: np.intersect1d(C.get_nodes(x), row.indices), coms)
    #print row.indices, [C.get_neighbors(x) for x in coms], com_intersect_row
    # 
    com_sum_a = map(lambda y: np.sum(row.data[np.in1d(row.indices, y)]), com_intersect_row)
    mods = np.multiply((1/m),com_sum_a) - np.multiply((1/(2*m**2)),np.multiply(k[i],com_sum_k))

    return zip(mods, coms)

def moveout_modularity(row, m, k, com, i):
    if len(com) > 1:
        mod = (-1/m)*np.sum(row[0, com].data) + (1/(2*m**2))*k[i]*np.sum(k[com]) - (k[i]**2)/(2*m**2) 
    else:
        mod = - (k[i]**2)/(2*m**2) 
    return mod


def get_max_gain(row, m, k, C, i):
    """
    returns the community c and the corresponding gain in modularity of moving
    vertex i there.
    """
    mods = movein_modularity(row, m, k, C, i)
    
    moveout = moveout_modularity(row, m, k, C.get_neighbors(i), i)
    
    mods = map(lambda x: (x[0] + moveout, x[1]), mods)

    #print mods
    new_mods = filter(lambda x: x[1] != C.get_community(i), mods) # speedup by putting this in movein?
    #print new_mods
    if new_mods:
        max_mod = max(new_mods)
        return max_mod[0], max_mod[1]
    else:
        return -1, -1

# Graveyard:
# coms = {C.get_community(a) : np.intersect1d(C.get_neighbors(a), row.indices) for a in row.indices} # these are interscted
# com_sum_a = map(lambda y: np.sum(row[0, y].data), com_intersect_row)
# com_intersect_row = map(lambda x: x in row_dict, coms)
# com_intersect_row = [filter(lambda x: x in row_dict, C.get_nodes(y)) for y in coms]
