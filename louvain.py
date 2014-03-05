from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse
import functions as fns
import time

def louvain(A, m, n, k, filewriter, cytowriter, analyzer, tsh, verbose, dump):
    i = 1
    old_q = mod.diagonal_modularity(A.diagonal(), k, m)
    t = time.time()
    while True:
        C = Communities(xrange(n), k)
        q = first_phase(A, m, n, k, C, old_q, tsh, verbose, i)
        coms = C.dict_renamed
        if filewriter:
            filewriter.write_nodelist(coms, n, i)
        if not (q > old_q):
            print 'It took %s seconds' % (time.time() - t)
            if not verbose:
                print "pass: %d. # of communities: %d. Q = %f" % (i-1,len(coms),q)
            if filewriter:
                filewriter.close()
                'Community structure outputted to .mat-file'
            if analyzer:
                analyzer.show()
                print 'CSD dumped to file'

            return
        A = second_phase(A, coms)
        n = A.shape[1]
        k = np.array(A.sum(axis=1)).reshape(-1,).tolist()

        if dump:
            C.dump(i)
        if cytowriter:
            cytowriter.add_pass(coms, A)
        if analyzer:
            analyzer.add_pass(coms)

        if verbose:
            print 'pass: %d. # of coms: %d. Q = %f' % (i, len(coms), q)

        old_q = q
        i += 1   

def first_phase(A, m, n, k, C, init_q, tsh, verbose, passnr):
    calc_modularity = mod.calc_modularity
    # noloops = mod.noloops_calc_modularity
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
    B = make_C_matrix(coms, A.shape[1])
    new = B.dot(A.dot(B.T))
    return new

def make_C_matrix(coms, n):
    # must make sure that dictionary is sorted
    keys = sorted(coms)
    ivec = np.array([k for k in keys for j in coms[k]])
    jvec = np.array([v for r in keys for v in coms[r]])
    vals = np.ones(len(jvec))
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(keys), n))
    return sparse.csr_matrix(coo)
