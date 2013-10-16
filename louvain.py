from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse
from itertools import chain


def louvain(A, m, n, k, filewriter):

    old_q = mod.modularity(A, k, m, [np.array([i]) for i in xrange(n)])
    while True:
        (coms,q) = first_phase(A, m, n, k, 0.001)
        #filewriter.write_array("".join(["com", str(i)]), C)
        #filewriter.write_array("".join(["q", str(i)]), q)
        print coms,q 
        A = second_phase(A, coms, n)

        n = A.shape[1]
        k = np.array(A.sum(1)).reshape(n)
        
        #q = mod.modularity(A, k, m, [np.array([i]) for i in xrange(n)])
        
        if not (q > old_q):
            return
        old_q = q   

def first_phase(A, m, n, k, tsh):
    C = Communities(range(n), k)
    new_Q = mod.modularity(A, k, m, C.get_communities())
    while True:
        old_Q = new_Q
        for i in xrange(n):
            row = A[i,:]
            (gain, c) = mod.get_max_gain(row, m, k, C, i)
            if gain > 0:
                print "moving %s to %s" %(i, c)
                #if i == 10 and c == 12:
                #    print gain, list(mod.movein_modularity(row, m, k, C, i)), mod.moveout_modularity(row, C, m, k, i), C.get_nodes(c), C.get_community_strength(c)
                C.move(i, c, k[i])
                new_Q += gain    
        if new_Q - old_Q < tsh:
            break
    return C.get_communities(), new_Q

def second_phase(A, coms, n):
    B = make_C_matrix(A, coms, n)
    return B.dot(A.dot(B.T))

def make_C_matrix(A, coms, n):
    ivec = [i for i,com in enumerate(coms) for j in com]
    jvec = list(chain.from_iterable(coms))
    vals = [1] * len(jvec)
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(coms), n))
    return sparse.csr_matrix(coo)
