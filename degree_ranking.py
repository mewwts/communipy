from operator import itemgetter
from collections import deque
from communities import Communities
from labels import Labels
from communities import Communities
import numpy as np
from modularity import get_gain
from utils import rank

def degree_rank(A, m, n, k, C, q, arguments):

    consider = rank(k)
    knbs = [set([]) for i in xrange(n)]
    not_seen = set(xrange(n))
    
    while True:
        new_q = degree_rank_inner(A, m, n, k, C, knbs, 
            consider, not_seen, q, arguments)
        not_seen = set(xrange(n))
        consider = rank([k[i] for i in 
            {node for j in not_seen for node in knbs[j]}])

        if new_q - q < arguments.tsh:
            break
        else:
            q = new_q

    return q

def degree_rank_inner(A, m, n, k, C, knbs, consider, not_seen, old_q, args):
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
