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
        (C,q) = first_phase(B, m, new_n, new_k, 0.001)
        filewriter.write_array("".join(["com", str(i)]), C)
        filewriter.write_array("".join(["q", str(i)]), q)
        if D:
            if len(D) == len(C):
                return
        D = C 
        i += 1
        B = second_phase(B, C, new_n)
        new_n = B.shape[1]
        new_k = k = np.array(B.sum(1)).reshape(new_n)

def first_phase(A, m, n, k, tsh):
    C = Communities(range(n))
    old_Q = mod.initial_modularity(A, k, m)
    new_Q = old_Q
    while True:
        old_Q = new_Q
        for i in xrange(n):
            row = A[i,:]
            (gain, c) = mod.get_max_gain(row, m, k, C, i)
            if gain > 0:
                #print "moving %s to %s" %(i, c)
                C.move(i, c)
                new_Q += gain
        if (new_Q - old_Q)/old_Q < 1 + tsh:
            break
    return filter(lambda c: len(c) > 0, C.get_communities()), new_Q

def second_phase(A, C, n):
    B = make_C_matrix(A, C, n)
    return B.dot(A.dot(B.T))


def make_C_matrix(A, C, n):
    lil_bow_wow = sparse.lil_matrix((len(C), n))
    for i,c in enumerate(C):
        for j in c:
            lil_bow_wow[i, j] = 1
    return sparse.csr_matrix(lil_bow_wow)