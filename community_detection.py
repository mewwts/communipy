from utils import Method
from communities import Communities
from modularity_communities import ModCommunities as ModComs
from louvain import louvain
from community_dissolve import community_dissolve
from degree_ranking import degree_rank
import modularity
import numpy as np
from scipy import sparse
import time

def community_detect(A, m, n, k, args):
    i = 1
    t = time.time()
    old_q = modularity.diagonal_modularity(A.diagonal(), k, m)

    while True:
        if args.method == Method.luv:
            C = Communities(xrange(n), k)
            q = louvain(A, m, n, k, C, old_q, args.tsh)
        elif args.method == Method.dissolve:
            C = ModComs(xrange(n), k, A, m)
            q = community_dissolve(A, m, n, k, C, old_q, args)
        elif args.method == Method.rank:
            C = Communities(xrange(n), k)
            q = degree_rank(A, m, n, k, C, old_q, args)

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


        A = community_network(A, coms)
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

def community_network(A, communities):
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

    B = community_affiliation_matrix(communities, A.shape[1])
    return B.dot(A.dot(B.T))

def community_affiliation_matrix(coms, n):
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
