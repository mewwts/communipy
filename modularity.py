import numpy as np

def initial_modularity(A, k, m):
    ks = reduce(lambda x,y: x+y, k**2)/(2*m)
    As = reduce(lambda x,y: x+y, A.diagonal())
    return (As - ks)/(2*m)


def movein_modularity(row, m, k, C, i):
    #row_dict = {}.fromkeys(row.indices)
    row_set = set(row.indices)   
    
    coms = np.unique(map(lambda x: C.get_community(x), row.indices))
    
    com_sum_k = map(lambda x: np.sum(k[C.get_nodes(x)]), coms)
    #com_intersect_row = map(lambda x: x in row_dict, coms)
    #com_intersect_row = [filter(lambda x: x in row.indices, C.get_nodes(y)) for y in coms]
    com_sum_a = map(lambda y: np.sum(row[0, y].data), com_intersect_row)
    
    mods = np.multiply((1/m),com_sum_a) - np.multiply((1/(2*m**2)),np.multiply(k[i],com_sum_k))
    return zip(mods, coms)

def alt_movein_modularity(row, m, k, C, i):
    """
    Should do everything with a dictionary to speed it up
    """
    row_set = set(row.indices)
    coms = {C.get_community(a) : np.intersect1d(C.get_neighbors(a), row.indices) for a in row.indices} # these are interscted
    com_sum_k = map(lambda x: np.sum(k[C.get_nodes(x)]), coms.keys())
    com_sum_a = map(lambda y: np.sum(row[0, y].data), coms.values())
    mods = np.multiply((1/m),com_sum_a) - np.multiply((1/(2*m**2)),np.multiply(k[i],com_sum_k))
    return zip(mods, coms.keys())


def moveout_modularity(row, m, k, com, i):
    mod = (-1/m)*np.sum(row[0, com].data) + (1/(2*m**2))*k[i]*np.sum(k[com]) -k[i]**2/(2*m**2) 
    return mod


def get_max_gain(row, m, k, C, i):
    """
    returns the community c and the corresponding gain in modularity of moving
    vertex node i there.
    """
    mods = movein_modularity(row, m, k, C, i)
    com = C.get_neighbors(i)
    if len(com) > 1:
        moveout = moveout_modularity(row, m, k, com, i)
        mods = map(lambda x: (x[0] + moveout, x[1]), mods)
    
    new_mods = filter(lambda x: x[1] != C.get_community(i), mods)

    if new_mods:
        max_mod = max(new_mods)
        return max_mod[0], max_mod[1]
    else:
        return -1, -1
