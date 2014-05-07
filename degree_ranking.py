# from __future__ import division
from operator import itemgetter
from collections import deque
from communities import Communities
from labels import Labels
from louvain import second_phase
from communities import Communities
import numpy as np
import modularity
import time

def rank(sequence):
    """ 
    Return the index from the original sequence the element
    has in the sorted array 

    """
    ranked = list(zip(*sorted(enumerate(sequence), key=itemgetter(1), reverse=True))[0])
    return ranked

def deg_rank_controller(A, m, n, k, arguments):

    t = time.time()
    C = Communities(xrange(n), k)
    q = modularity.diagonal_modularity(A.diagonal(), k, m)
    consider = rank(k)
    knbs = [set([]) for i in xrange(n)]
    not_seen = set(xrange(n))
    # moved = set([1]) # dummy
    
    while True:
        new_q = degree_rank(A, m, n, k, C, knbs, 
            consider, not_seen, q, arguments)
        not_seen = set(xrange(n))
        consider = rank([k[i] for i in 
            {node for j in not_seen for node in knbs[j]}])

        if new_q - q < arguments.tsh:
            break
        else:
            q = new_q

    if arguments.exporter:
        arguments.exporter.write_nodelist(C.dict_renamed)

    print C.dict
    print("Modularity = {}".format(q))
    print('It took %s seconds' % (time.time() - t))

def degree_rank(A, m, n, k, C, knbs, consider, not_seen, old_q, args):
    """
    Finds the communities of A by the degree-rank method.

    Args: 

    A: Adjacency matrix stored in CSR format.
    m: 0.5 * A.sum(), the total weight of the graph.
    n: the number of vertices in the graph. A.shape[1]
    k: degree sequence of the graph. Rowsum/Colsum.
    C: community structure
    knbs: list of the high degree neighbors of vertex i
    not_seen: set of nodes marked as not not seen
    consider: the vertices we are considering
    args: Namedtuple with args parsed by main.

    Returns:

    C: Community object

    """
    q = old_q
    moved = set([])
    index = 0

    queue = deque([consider[index]])
    while queue:
        i = queue.popleft()
        not_seen.discard(i)
        nbs = A.indices[A.indptr[i]:A.indptr[i+1]]

        for j in nbs:
            if j in moved:
                continue
            not_seen.discard(j)
            knbs[j].add(i)
            data = A.data[A.indptr[j]:A.indptr[j+1]]
            indices = A.indices[A.indptr[j]:A.indptr[j+1]]
            if C.nodes[i] != C.nodes[j]:
                movein, moveout = get_gain(data, indices, m, k, C, j, C.nodes[i])
                if movein + moveout > 0:
                    moved.add(j)
                    C.move(j, C.nodes[i], k[j])
                    q += movein - moveout

        if not_seen:
            index += 1
            try:
                next = consider[index]
            except IndexError:
                return q
            else:
                queue.append(next)
    return q

def get_gain(data, indices, m, k, C, i, com):
    """
    Calculates and returns the gain of moving i to com.

    Args:
    i: the integer label of the vertex to be moved
    c_j: the label of the proposed community
    C: the community object

    Returns:
    A float representing the modularity of the move.

    """
    k_i = k[i]
    c_i = C.affiliation(i)
    const = k_i/(2.0*m**2)
    movein = - const*C.strength[com]
    moveout = (2.0/(4.0*m**2))*k_i*(C.strength[c_i] - k_i)
    for ind,j in enumerate(indices): 
        
        c_j = C.affiliation(j)
        if c_j == c_i:
            if i != j:
                moveout -= data[ind]/m
            continue
        elif c_j == com:
            movein += data[ind]/m

    return movein, moveout
