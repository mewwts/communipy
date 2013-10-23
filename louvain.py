from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse


def louvain(A, m, n, k, filewriter):

    i = 1
    old_q = mod.diagonal_modularity(A.diagonal(), k, m) 
    while True:
        C = Communities(xrange(n), k)
        (coms,q) = first_phase(A, m, n, k, C, 0.001)
        #filewriter.write_array("".join(["com_", str(i)]), C.get_communities_renamed())
        #filewriter.write_array("".join(["q_", str(i)]), q)
        print coms, q
        A = second_phase(A, coms, n)
        n = A.shape[1]
        k = np.array(A.sum(1)).reshape(n)
        if not (q > old_q):
            print i
            return
        old_q = q
        i += 1   

def first_phase(A, m, n, k, C, tsh):
    
    get_max_gain = mod.get_max_gain
    move = C.move

    new_Q = mod.diagonal_modularity(A.diagonal(), k, m)
    
    while True:
        old_Q = new_Q
        for i in xrange(n):
            row = A[i,:]
            (c, gain) = get_max_gain(row, m, n, k, C, i)
            if gain > 0:
                print "moving %s to %s" %(i, c)
                move(i, c, k[i])
                new_Q += gain    
        if new_Q - old_Q < tsh:
            break
    return C.get_communities_renamed(), new_Q

def second_phase(A, coms, n):
    B = make_C_matrix(A, coms, n)
    new = B.dot(A.dot(B.T))
    return new

def make_C_matrix(A, coms, n):
    # must make sure that dict is sorted
    keys = sorted(coms)
    ivec = np.array([k for k in keys for j in coms[k]])
    #ivec = [i for i,com in enumerate(coms) for j in com]
    jvec = np.array([v for r in keys for v in coms[r]])
    #jvec = list(chain.from_iterable(coms))
    vals = np.array([1] * len(jvec))
    coo = sparse.coo_matrix((vals, (ivec, jvec)), shape=(len(coms), n))
    return sparse.csr_matrix(coo)
