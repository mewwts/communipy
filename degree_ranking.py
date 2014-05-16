from collections import deque
from modularity import get_gain
from utils import rank

def degree_rank(G, C, q, arguments):

    k = G.k
    n = G.n
    consider = rank(k) 
    knbs = [set([]) for i in xrange(n)]
    not_seen = set(xrange(n))
    
    while True:
        new_q = degree_rank_inner(G, C, knbs, 
            consider, not_seen, q, arguments)
        # not_seen = set(xrange(n))
        # consider = rank([k[i] for i in 
        #     {node for j in not_seen for node in knbs[j]}])        
        if new_q - q < arguments.tsh:
            break
        q = new_q

    return new_q

def degree_rank_inner(G, C, knbs, consider, not_seen, old_q, args):
    """
    Finds the communities of A by the degree-rank method.

    Args: 

    G: Graph object
    C: community structure
    knbs: list of the high degree neighbors of vertex i
    not_seen: set of nodes marked as not not seen
    consider: the vertices we are considering
    args: Namedtuple with args parsed by main.

    Returns:

    q: modularity

    """
    A, m, n, k = G
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
            not_seen.discard(j) # We've seen j
            knbs[j].add(i) # i is a high-degree nb of j
            if C.nodes[i] != C.nodes[j]:
                movein, moveout = get_gain(G, C, j, C.nodes[i])
                if movein + moveout > 0:
                    moved.add(j)
                    C.move(j, C.nodes[i], k[j])
                    q += movein + moveout

        if not_seen:
            try:
                while True:
                    index += 1
                    next = consider[index]
                    if next not in moved:
                        break
            except IndexError:
                return q
            queue.append(next)
        else:
            return q
