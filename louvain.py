from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse
import functions as fns
import time

def louvain(A, m, n, k, args):
    """
    Find the communities of the graph represented by A using the Louvain
    method.

    Args:
    A: Adjacency matrix in CSR format
    m: 0.5 * A.sum()
    n: A.shape[1] the number of vertices in the graph
    k: degree sequence
    args: flags and objects for data export etc.

    """
    i = 1
    old_q = mod.diagonal_modularity(A.diagonal(), k, m)
    t = time.time()

    while True:
        C = Communities(xrange(n), k)
        q = first_phase(A, m, n, k, C, old_q, args.tsh)
        coms = C.dict_renamed
        if args.exporter:
            args.exporter.write_nodelist(coms)

        if not (q > old_q):
            print 'It took %s seconds' % (time.time() - t)
            if not args.verbose:
                print "pass: %d. # of communities: %d. Q = %f" % (i-1,len(coms),q)
            if args.exporter:
                args.exporter.close()
                print('Community structure outputted to .txt-file')
            if args.analyzer:
                args.analyzer.show()
                print 'CSD dumped to file'
            return

        A = second_phase(A, coms)
        n = A.shape[1]
        k = np.array(A.sum(axis=1)).reshape(-1,).tolist()

        if args.dump:
            C.dump(i)
        if args.cytowriter:
            args.cytowriter.add_pass(coms, A)
        if args.analyzer:
            args.analyzer.add_pass(coms)

        if args.verbose:
            print 'pass: %d. # of coms: %d. Q = %f' % (i, len(coms), q)

        old_q = q
        i += 1   

def first_phase(A, m, n, k, C, init_q, tsh):
    """
    The first phase of the Louvain method is looping through the 
    vertices of the graph and establishing communities until a whole
    moving vertices only have a negliable modularity gain

    Args:
    A: Adjacency matrix in CSR format
    m: 0.5 * A.sum()
    n: A.shape[1], the number of vertices in the graph
    k: degree sequence, k[i] is the degree of vertex i
    C: Community object
    init_q: the modularity of the network at the time of function start
    tsh: float value indicating the treshold for negliable gain.

    Returns:
    new_q: the modularity after all changes.
    """

    calc_modularity = mod.calc_modularity
    move = C.move
    new_q = init_q 
    
    while True:
        old_q = new_q
        
        for i in fns.yield_random_modulo(n):
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]
            (c, gain) = calc_modularity(data, indices, m, k, C, i)
            if gain > 0:
                move(i, c, k[i])
                new_q += gain

        if new_q - old_q < tsh:
            break
    return new_q

def second_phase(A, coms):
    """
    The second phase of the Louvain algorithms consists of making the
    community network in which the communities of the first phase are 
    nodes in a new network.

    Args:
    A: Adjacency matrix of the graph
    coms: A dictionary with keys from 0 to n-1. Values are lists of
          nodes.

    Returns:
    B: Adjacency matrix of the community network

    """

    B = make_C_matrix(coms, A.shape[1])
    new = B.dot(A.dot(B.T))
    return new

def make_C_matrix(coms, n):
    """
    Constructing the matrix of community affiliation. Entry ij indicates
    that vertex i is in community j.

    Args:
    coms: A dictionary with keys from 0 to n-1. Values are lists of
          nodes.
    n: The number of vertices in the graph. A.shape[1]

    Returns:
    A csr matrix indicating community affiliation of vertex i. Each row
    has one 1-entry, and is per node. The columns are communities.

    """
    # must make sure that dictionary is sorted
    keys = sorted(coms)
    ivec = np.array([k for k in keys for j in coms[k]])
    jvec = np.array([v for r in keys for v in coms[r]])
    vals = np.ones(len(jvec))
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(keys), n))
    return sparse.csr_matrix(coo)
