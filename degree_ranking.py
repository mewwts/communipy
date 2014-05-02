# from __future__ import division
from operator import itemgetter
from collections import deque
from communities import Communities
from labels import Labels
from louvain import second_phase
from modularity_communities import ModCommunities as ModComs
import numpy as np
import modularity
import time

def rank(tuples):
    """
    Ranks the vertices in 'k' based on the magnitude of the elements.

    Args:

    tuples: list of tuples to sort and rank
    
    Returns:

    A list of tuples (i, tuples[i]) sorted in decreasing order
    
    """
    # k_tuples = [(i, k[i]) for i in xrange(len(k))]
    return [i for i, j in sorted(tuples, key=itemgetter(1), reverse=True)]

def deg_rank_controller(A, m, n, k, arguments):
    t = time.time()
    C = ModComs(xrange(n), k, A, m)
    consider = rank([(i, k[i]) for i in xrange(len(k))])
    knbs = [set([]) for i in xrange(n)]
    not_seen = set(xrange(n))
    moved = set([1]) # dummy
    
    while len(moved) > 0:
        moved = degree_rank(A, m, n, k, C, knbs, consider, not_seen, arguments)
        # not_seen = {i for i in xrange(n) if C.d[i] == max(C.d) or len(C[C.nodes[i]]) == 1}
        not_seen = set(xrange(n))
        consider = rank([(i, k[i]) for i in 
            {node for j in not_seen for node in knbs[j]}])
        # print("consider {}".format(consider))
        # print("not_seen {}".format(not_seen))
    if arguments.exporter:
        arguments.exporter.write_nodelist(C.dict_renamed)
    print C.dict
    print('It took %s seconds' % (time.time() - t))

def degree_rank(A, m, n, k, C, knbs, consider, not_seen, args):
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
                    C.move(j, C.nodes[i], k[j], movein, moveout, 0.0)
                    C.d[j] = C.d[i] + 1
        if not_seen:
            index += 1
            try:
                next = consider[index]
            except IndexError:
                return moved
            else:
                queue.append(next)

    return moved

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
