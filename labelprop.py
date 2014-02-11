from operator import itemgetter
from communities import Communities
import modularity
from math import exp
import random

def labelprop(A, m, n, k):
    C = Communities(xrange(n), k)
    
    while True:
        propagate(A, m, n, k, C)
        print C.get_communities_renamed()
        print modularity.modularity(A, k, m, C)
        return


def propagate(A, m, n, k, C):
    get_com = C.get_community
    b = [-1] * n
    f = [1.0/n] * n
    num_moves = 1000

    while num_moves > 0:
        num_moves = 0
        for i in xrange(n):
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]
            my_com = 0
            neighbor_coms = {}
            c_i = get_com(i)

            for ind, j in enumerate(indices):
                b[j] = sigmoid(float(j+1)/n)
                c_j = get_com(j)
                if c_i == c_j:
                    if i != j:
                        my_com += data[ind]
                    continue
                
                if c_j in neighbor_coms:
                    neighbor_coms[c_j] += f[j]*b[j]*data[ind]
                else:
                    neighbor_coms[c_j] = f[j]*b[j]*data[ind]

            if neighbor_coms:
                best_match = max((i for i in neighbor_coms.iteritems()), key=itemgetter(1))[0]
                if neighbor_coms[best_match] > my_com:
                    C.move(i, best_match, k[i])
                    num_moves += 1
                    f[i] = neighbor_coms[best_match] * b[best_match]

def sigmoid(t):
    etta = 2.0
    lamb = 0.5
    return 1.0 / (1 + exp(-etta*(t-lamb)))
