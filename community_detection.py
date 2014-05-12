from utils import Method
from communities import Communities
from modularity_communities import ModCommunities as ModComs
from louvain import louvain
from dissolve import community_dissolve
from degree_ranking import degree_rank
import modularity
import numpy as np
from utils import Graph
from scipy import sparse
import time

def community_detect(G, args):

    i = 1
    t = time.time()
    old_q = modularity.diagonal_modularity(G.A.diagonal(), G.k, G.m)

    while True:
        if args.method == Method.luv:
            C = Communities(xrange(G.n), G.k)
            q = louvain(G, C, old_q, args.tsh)
        elif args.method == Method.dissolve:
            C = ModComs(xrange(G.n), G)
            q = community_dissolve(G, C, old_q, args)
        elif args.method == Method.rank:
            C = Communities(xrange(G.n), G.k)
            q = degree_rank(G, C, old_q, args)
        else:
            raise Exception("What are you doing here.")

        coms = C.dict_renamed
        
        if args.exporter:
            args.exporter.write_nodelist(coms)
        
        if not (q > old_q):
            print("It took {} seconds".format(time.time() - t))
            if not args.verbose:
                print("pass: {}. # of communities: "
                      "{}. Q = {}".format(i-1, len(coms), q))
            if args.exporter:
                args.exporter.close()
                print('Community structure outputted to .txt-file')
            if args.analyzer:
                args.analyzer.show()
                print 'CSD dumped to file'
            return


        A = community_network(G.A, coms)
        k = np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist()
        m = 0.5*A.sum()
        n = A.shape[0]
        G = Graph(A, m, n, k)

        if args.dump:
            C.dump(i)
        if args.cytowriter:
            args.cytowriter.add_pass(coms, G.A)
        if args.analyzer:
            args.analyzer.add_pass(coms)

        if args.verbose:
            print("pass: {}. # of coms: {}. Q = {}".format(i, len(coms), q))

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
