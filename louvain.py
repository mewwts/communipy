from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse


def louvain(A, m, n, k, filewriter, tsh):

    i = 1
    old_q = mod.diagonal_modularity(A.diagonal(), k, m) 
    while True:
        C = Communities(xrange(n), k)
        (C,q) = first_phase(A, m, n, k, C, old_q, tsh)
        # filewriter.write_array("".join(["com_", str(i)]), C.get_communities_renamed())
        # filewriter.write_array("".join(["q_", str(i)]), q)
        coms = C.get_communities_renamed()
        print len(coms), q
        C.dump(i)
        A = second_phase(A, coms, n)
        n = A.shape[1]
        k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]
        
        if not (q > old_q):
            print i
            # print mod.diagonal_modularity(A.diagonal(), k, m)
            return
        
        old_q = q
        i += 1   

def first_phase(A, m, n, k, C, init_q, tsh):
    
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
                # print "moving %s to %s" %(i, c)
                move(i, c, k[i])
                new_q += gain

        print 'there are %d communities' % C.get_number_of_communities()
        print 'newQ = %f, oldQ = %f' %(new_q, old_q)

        if new_q - old_q < tsh:
            break
    return C, new_q

def second_phase(A, coms, n):
    B = make_C_matrix(A, coms, n)
    new = B.dot(A.dot(B.T))
    return new

def make_C_matrix(A, coms, n):
    # must make sure that dict is sorted
    keys = sorted(coms)
    ivec = np.array([k for k in keys for j in coms[k]])
    jvec = np.array([v for r in keys for v in coms[r]])
    vals = np.array([1] * len(jvec))
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(keys), n))
    return sparse.csr_matrix(coo)
