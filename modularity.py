from collections import defaultdict
import numpy as np
import numexpr as nr
from operator import itemgetter

def diagonal_modularity(diag, k, m):
    """Calculates the modularity when all vertices are in their own community"""
    ks = np.array(k)
    return (1.0/(2*m))*nr.evaluate("sum(diag)") -(1/(4*m**2))*nr.evaluate("sum(ks**2)")

def modularity(G, C):
    """ 
    Calculates the global modularity by summing over each community. 
    It is very slow, use louvain.second_phase and diagonal_modularity
    instead

    """
    A, m, n, k = G
    q = 0.0
    for com, c in C:
        rowslice = A[c,:]
        data = rowslice.data
        indices = rowslice.indices
        q += ((1.0/(2*m))*np.sum(data[np.in1d(indices, c)]) -
             (C.strength[com]/(2*m))**2)
    return q

def single_node_modularity(G, i):
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
    return G.A[i,i]/(2*G.m) - (G.k[i]/(2*G.m))**2

def modularity_of_partition(A, k, m, nodes):
    rowslice = A[nodes,:]
    data = rowslice.data
    indices = rowslice.indices
    q = ((1.0/(2*m))*np.sum(data[np.in1d(indices, nodes)]) -
         (sum(k[i] for i in nodes)/(2*m))**2)
    return q

def modularity_gain(G, C, i):
    """"
    Calculates the modularity gain of moving vertex i into the 
    community of its neighbors.

    """
    A, m, n, k = G
    indices = A.indices[A.indptr[i]:A.indptr[i+1]]
    data = A.data[A.indptr[i]:A.indptr[i+1]]

    movein = {}
    k_i = k[i]
    c_i = C.nodes[i]
    const = k_i/(2.0*m**2)
    moveout = (2.0/(4.0*m**2))*k_i*(C.strength[c_i] - k_i)
    max_movein = (-1, -1.0)
    for ind,j in enumerate(indices):
        aij = data[ind]
        c_j = C.nodes[j]
        if c_j == c_i:
            if i != j:
                moveout -= aij/m
            continue

        if c_j in movein:
            movein[c_j] += aij/m
        else:
            movein[c_j] = aij/m - const*C.strength[c_j]

        if movein[c_j] > max_movein[1]:
            max_movein = (c_j, movein[c_j])

    if not movein:
        return (-1, -1.0, 0.0)

    return (max_movein[0], max_movein[1],  moveout)

def get_gain(G, C, i, dest):
    """
    Calculates and returns the gain of moving i to dest.

    Args:
    i: the integer label of the vertex to be moved
    dest: the label of the proposed community
    C: the community object

    Returns:
    A float representing the modularity of the move.

    """
    A, m, n, k = G
    data = A.data[A.indptr[i]:A.indptr[i+1]]
    indices = A.indices[A.indptr[i]:A.indptr[i+1]]
    k_i = k[i]
    c_i = C.nodes[i]
    movein = - k_i*C.strength[dest]/(2.0*m**2)
    moveout = (2.0/(4.0*m**2))*k_i*(C.strength[c_i] - k_i)
    for ind,j in enumerate(indices): 
        aij = data[ind]
        c_j = C.nodes[j]
        if c_j == c_i:
            if i != j:
                moveout -= aij/m
            continue
        elif c_j == dest:
            movein += aij/m

    return movein, moveout

def mass_modularity(G, C, nodes, c):
    """
    Calculates the modularity gain of moving each of the nodes 
    to the best match.

    Args:
    G: Graph object
    nodes: list of nodes in community
    C: Community structure
    c: original affiliation of nodes

    Returns:
    node2c: dict holding best match for vertex i
    c2node: dict holding the vertices going to community c
    dqins: holds the global gain of moving vertex i to node2c[i].
    dqouts: holds the global loss of  --"--
    quv: the modularity of the subsets that is moved. If only one vertex
         is moved to a community, this is q_i.
    best_move: the (node, community) move that has the highest
               modularity gain associated to it

    """
    A, m, n, k = G

    node2c = {}
    c2node = defaultdict(set)
    dqins = {}
    dqouts = {}
    quv = defaultdict(float)
    best_move = (-1, -1)

    for i in nodes:
        indices = A.indices[A.indptr[i]:A.indptr[i+1]]
        data = A.data[A.indptr[i]:A.indptr[i+1]]
        nbs = set([])
        crossterms = defaultdict(float)
        movein = {}
        k_i = k[i]
        moveout = -2*k_i*C.strength[c]/((2*m)**2)
        max_movein = (-1, 0.0)

        for ind, j in enumerate(indices):
            aij = data[ind]
            k_j = k[j]
            c_j = C.nodes[j]
            if c_j == c:
                moveout += aij/m

                try:
                    nc_j = node2c[j]
                except KeyError:
                    continue
                else:
                    if nc_j != -1:
                        qij = aij/(2*m) - (k_i*k_j)/(2*m)**2
                        nbs.add(j)
                        crossterms[nc_j] += 2*qij
                continue

            try:
                movein[c_j] += aij/m
            except KeyError:
                movein[c_j] = aij/m - 2*k_i*C.strength[c_j]/(2*m)**2

            if movein[c_j] > max_movein[1]:
                max_movein = (c_j, movein[c_j])

        dest, q_in = max_movein
        node2c[i] = dest
        c2node[dest].add(i)
        dqins[i] = q_in
        dqouts[i] = moveout

        if q_in - moveout > best_move[1]:
            best_move = (i, q_in - moveout)

        qi = C.node_mods[i]
        quv[dest] += qi
        quv[dest] += crossterms[dest]

        for node in c2node[dest] - (nbs | set([i])):
            qij = -2*k[i]*k[node]/(2*m)**2
            quv[dest] += qij

    return node2c, c2node, dqins, dqouts, quv, best_move[0]