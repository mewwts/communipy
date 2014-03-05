from labels import Labels
from louvain import second_phase
import modularity
import functions as fns
import numpy as np
import sys
from collections import defaultdict
import numexpr as nr


def dpa(A, m, n, k):

    # Run defensive dalpa on the network    
    C = Labels(xrange(n), k)
    dalpa(A, m, n, k, C, False)
    print "we are in dpa, numcoms: ", len(C.dict_renamed)
    

    # Construct community network, and run offensive dalpa
    B = second_phase(A, C.dict_renamed)
    bn = B.shape[1]
    bk = k = np.array(B.sum(axis=1)).reshape(-1,).tolist()

    BC = Labels(xrange(bn), bk)
    dalpa(B, m, bn, bk, BC, True)
    
    print "processed community network, numcoms ", len(BC.dict_renamed)
    newcoms = None

    if len(BC.get_communities()) == 1:
         print 'continuing with modified bdpa'
         bdpa_modified(A, m, n, k, C)
    else:
        # extract the largest community in terms of nodes from PASS 0
        return

    
    if newcoms is not None:
        for com, nodes in newcoms.iteritems():
            orgnodes = Anodes[nodes]
            C.insert_community(orgnodes, k[orgnodes])
    
    communities = C.dict_renamed
    
    return communities, modularity.modularity(A, k, m, C)

def dalpa(A, m, n, k, C, offensive=False):
    """s
    Defensive/Offensive label propagation. 

    """

    # initialize some variables
    delta = 0.0
    num_iter = 1
    num_moves = 1
    # while not convergence
    while num_moves > 0:
        num_moves = 0

        for i in fns.yield_random_modulo(n):

            c_i = C.affiliation(i)
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]

            neighbor_coms = defaultdict(float)
            max_neighbor = (-1, -1.0)
            com_edges = defaultdict(float)
            d_dict = defaultdict(lambda: sys.maxint)
            p_dict = defaultdict(float)

            for ind, j in enumerate(indices):
                c_j = C.affiliation(j)
                p_j = C.p[j]

                if i == j:
                    continue

                d = C.d[j]
                if d < d_dict[c_j]:
                    d_dict[c_j] = d

                if not offensive:
                    neighbor_coms[c_j] += p_j*(1 - delta*d)*data[ind]
                    p_dict[c_j] += p_j/C.internal[j]
                else:
                    neighbor_coms[c_j] += (1 - p_j)*(1 - delta*d)*data[ind]
                    p_dict[c_j] += p_j/k[j]

                if neighbor_coms[c_j] > max_neighbor[1]:
                    max_neighbor = (c_j, neighbor_coms[c_j])

                com_edges[c_j] += data[ind]

            # Move to the best community
            best_match, best_val = max_neighbor
            if best_match == -1:
                print("Best match == -1... Hmmm")
                continue
            if best_match != c_i and best_val > neighbor_coms[c_i]:

                C.move(i, best_match, k[i], com_edges[best_match])
                C.d[i] = d_dict[best_match] + 1

                if not (offensive and num_iter <= 1):                
                    C.p[i] = p_dict[best_match]
                num_moves += 1

        num_iter += 1
        delta = float(num_moves) / n
        if delta >= 0.5:
            delta = 0.0

def bdpa_modified(A, m, n, k, C):
    coms = C.dict_renamed
    for c, nodes in coms.iteritems():
        p_list = [C.p[j] for j in nodes]
        for i in C[c]:
            if C.p[i] <= np.median(p_list):
                C.move(i, -1, k[i])
                C.d[i] = 0
                C.p[i] = 0
    dalpa(A, m, n, k, C, True)

def bdpa(A, m, n, k, C):
    dalpa(A, m, n, k, C, False)
    bdpa_modified(A, m, n, k, C)
