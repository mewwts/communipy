import numpy as np
import numexpr as nr
from operator import itemgetter

def diagonal_modularity(diag, k, m):
    """Calculates the modularity when all vertices are in their own community"""
    ks = np.array(k)
    return (1.0/(2*m))*nr.evaluate("sum(diag)") -(1/(4*m**2))*nr.evaluate("sum(ks**2)")
    
def modularity(A, k, m, C):
    """ 
    Calculates the global modularity by summing over each community. 
    It is very slow, use louvain.second_phase and diagonal_modularity
    instead

    """
    q = 0.0
    for com, c in C:
        rowslice = A[c,:]
        data = rowslice.data
        indices = rowslice.indices
        q += ((1.0/(2*m))*np.sum(data[np.in1d(indices, c)]) -
             (C.strength[com]/(2*m))**2)
    return q

def single_node_modularity(A, k, m, i):
    """
    Calculates the modularity of an isolated node.
    Args:

    A: Adjacency matrix of the graph
    k: Degree sequence of the graph
    m: The total weight of the graph. 0.5 * A.sum()
    i: the vertex considered

    Returns:
    A float representing the modularity of the isolated node.

    """
    return A[i,i]/(2*m) - (k[i]/(2*m))**2

def modularity_of_partition(A, k, m, nodes):
    """
    Calculates the modularity of the partition defined by nodes.

    Args:

    A: Adjacency matrix of the graph
    k: Degree sequence of the graph
    m: The total weight of the graph. 0.5 * A.sum()
    nodes: The vertices in the partition

    Returns:

    The modularity of the partition.

    Raises:
    TypeError when nodes is not a list or np.array

    """

    ks = np.array([k[i] for i in nodes])
    nodes = list(nodes)
    data = A[nodes, :][:, nodes].data
    if len(data) == 0:
        data = np.array([0.0])
    q = (1.0/(2*m) * nr.evaluate("sum(data)") -
            ((1.0/(4*m**2))*nr.evaluate("sum(ks**2)")))
    return q

def calc_modularity(data, indices, m, k, C, i):
    """"
    Calculates the modularity gain of moving vertex i into the 
    community of its neighbors

    """
    movein = {}
    k_i = k[i]
    c_i = C.affiliation(i)
    const = k_i/(2.0*m**2)
    moveout = (2.0/(4.0*m**2))*k_i*(C.strength[c_i] - k_i)
    max_movein = (-1, -1.0)
    for ind,j in enumerate(indices):

        c_j = C.affiliation(j)
        if c_j == c_i:
            if i != j:
                moveout -= data[ind]/m
            continue

        if c_j in movein:
            movein[c_j] += data[ind]/m
        else:
            movein[c_j] = data[ind]/m - const*C.strength[c_j]

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
