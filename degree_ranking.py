from modularity import get_gain
from utils import rank

def degree_rank(G, C, q, arguments):
    """ Finds the communities of A by the degree-rank method. """
    consider = rank(G.k) 
    not_seen = set(xrange(G.n))
    while True:
        new_q, moved = degree_rank_inner(G, C, 
                                         consider, not_seen, q, arguments)
        not_seen = set(xrange(G.n))
        if new_q - q <= arguments.tsh:
            break
        q = new_q
    return new_q

def degree_rank_inner(G, C, consider, not_seen, old_q, args):
    """
    Establish communities around the vertices specified in consider.

    Args: 

    G: Graph object
    C: Community structure
    consider: The vertices we are establish communities around
    not_seen: Set of nodes marked as not not seen
    old_q: The modularity of the network when this function is called
    args: Namedtuple of arguments

    Returns:
    q: modularity of the network

    """
    A, m, n, k = G
    q = old_q
    moved = set([])
    index = 0
    i = consider[index]

    while True:
        not_seen.discard(i)
        nbs = A.indices[A.indptr[i]:A.indptr[i+1]]
        for j in nbs:
            not_seen.discard(j) 
            if C.nodes[i] != C.nodes[j] and j not in moved:
                movein, moveout = get_gain(G, C, j, C.nodes[i])
                if movein + moveout > 0:
                    moved.add(j)
                    moved.add(i)
                    C.move(j, C.nodes[i], k[j])
                    q += movein + moveout

        if not_seen:
            while True:
                index += 1
                try:
                    next = consider[index]
                except IndexError:
                    return q, moved
        
                if next not in moved:
                    i = next
                    break
        else:
            return q, moved
