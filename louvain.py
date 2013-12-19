from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse
import time 
import networkx as nx

def louvain(A, m, n, k, filewriter, cytowriter, analyzer, tsh, verbose, dump):

    i = 1
    old_q = mod.diagonal_modularity(A.diagonal(), k, m) 
    t = time.time()
    while True:
        C = Communities(xrange(n), k)
        (C,q) = first_phase(A, m, n, k, C, old_q, tsh, verbose)
        if filewriter:
            filewriter.write_nodelist(C.get_communities_renamed(), n, i)
        coms = C.get_communities_renamed()

        if not (q > old_q):
            print 'It took %s seconds' % (time.time() - t)
            if not verbose:
                print "pass: %d. # of comms: %d. Q = %f" % (i,len(coms),q)
            if filewriter:
                filewriter.close()
                'Community structure outputted to .mat-file'
            if analyzer:
                analyzer.show()
                print 'CSD dumped to file'
            return
        A = second_phase(A, coms, n)
        n = A.shape[1]
        k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]

        if dump:
            C.dump(i)
        if cytowriter:
            cytowriter.add_pass(coms, A)
        if analyzer:
            analyzer.add_pass(coms)

        if verbose:
            print 'pass: %d. # of comms: %d. Q = %f' % (i,len(coms),q)

        old_q = q
        i += 1   

def first_phase(A, m, n, k, C, init_q, tsh, verbose):
    
    calc_modularity = mod.calc_modularity
    move = C.move
    new_q = init_q 
    
    while True:
        old_q = new_q
        
        for i in xrange(n):
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]
            (c, gain) = calc_modularity(data, indices, m, k, C, i)
            if gain > 0:
                move(i, c, k[i])
                new_q += gain

        if new_q - old_q < tsh:
            break
    return C, new_q

def second_phase(A, coms, n):
    # This is slow in Python. Consider making it directly with a coo-sparse.
    B = make_C_matrix(A, coms, n)
    new = B.dot(A.dot(B.T))
    return new

def make_C_matrix(A, coms, n):
    # must make sure that dict is sorted
    keys = sorted(coms)
    ivec = np.array([k for k in keys for j in coms[k]])
    jvec = np.array([v for r in keys for v in coms[r]])
    vals = np.ones(len(jvec))
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(keys), n))
    return sparse.csr_matrix(coo)
