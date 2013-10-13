from communities import Communities
import modularity as mod
import numpy as np
from scipy import sparse


def louvain(A, m, n, k, filewriter):
    B = A
    new_n = n
    new_k = k
    i = 1
    D = None
    while True:
        (C,q) = first_phase(B, m, new_n, new_k, 0.03)
        #filewriter.write_array("".join(["com", str(i)]), C)
        #filewriter.write_array("".join(["q", str(i)]), q)
        if D:
            if len(D) == len(C):
                print "D %s" % D
                print "C %s" % C
                return
        D = C 
        i += 1
        B = second_phase(B, C, new_n)
        new_n = B.shape[1]
        new_k = k = np.array(B.sum(1)).reshape(new_n)

def first_phase(A, m, n, k, tsh):
    C = Communities(range(n))
    new_Q = mod.initial_modularity(A, k, m)
    while True:
        old_Q = new_Q
        for i in xrange(n):
            row = A[i,:]
            (gain, c) = mod.get_max_gain(row, m, k, C, i)
            if gain > 0:
                print "moving %s to %s" %(i, c)
                C.move(i, c)
                new_Q += gain    
        if new_Q - old_Q < tsh:
            break
    return C.get_non_empty_communities(), new_Q

def second_phase(A, coms, n):
    B = make_C_matrix(A, coms, n)
    return B.dot(A.dot(B.T))

#do this with COO matrix instead
def make_C_matrix(A, coms, n):
    lil = sparse.lil_matrix((len(coms), n))
    for i,c in enumerate(coms):
        for j in c:
            lil[i, j] = 1
    return sparse.csr_matrix(lil)
