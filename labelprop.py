import time
from operator import itemgetter
from communities import Communities
from louvain import second_phase
import modularity
import functions as fns
import numpy as np
from collections import defaultdict

def dpa(A, m, n, k):
    C = Communities(xrange(n), k)
    bdpa(A, m, n, k, C)
    # print C.get_communities()
    print modularity.modularity(A, k, m, C)
    # dalpa(A, m, n, k, C, False)
    # dalpa has now changed our Community-object. 
    
    # Construct community network
    # B = second_phase(A, C.get_communities_renamed())
    # bn = B.shape[1]
    # bk = [float(B.data[B.indptr[j]:B.indptr[j+1]].sum()) for j in xrange(bn)]
    # BC = Communities(xrange(bn), bk)
    # dalpa(B, m, bn, bk, BC, True)
    
    # if len(BC.get_communities()) == 1:
    #     bdpa(A, m, n, k, C)
    # else:
    #     largest = max(((len(l),c) for c,l in BC.get_communities().iteritems()))[1]
    #     nodes = BC.get_nodes(largest)
    #     D = B[nodes,:][:, nodes]
    #     dm = 0.5 * D.sum()
    #     dn = D.shape[1]
    #     dk = [float(D.data[D.indptr[j]:D.indptr[j+1]].sum()) for j in xrange(dn)]
    #     # This will not work. very well
    #     dpa(D, dm, dn, dk)

    # print C.get_communities_renamed()
    # 
    return

def dalpa(A, m, n, k, C, offensive=False):
    """
    Defensive/Offensive label propagation. 

    """
    # function references
    get_com = C.get_community
    get_p = C.get_p
    get_d = C.get_d

    # initialize some variables
    delta = 0.0
    num_iter = 1
    intra_com = k[:]
    num_moves = 1

    # while not convergence
    while num_moves > 0:
        num_moves = 0
        for i in fns.yield_random_modulo(n):
            c_i = get_com(i)
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]
            neighbor_coms = defaultdict(int)
            com_edges = defaultdict(int)

            for ind, j in enumerate(indices):
                c_j = get_com(j)
                if i == j:
                    continue

                if not offensive:
                    neighbor_coms[c_j] += get_p(j)*(1 - delta*get_d(j))*data[ind]
                else: 
                    neighbor_coms[c_j] += (1 - get_p(j))*(1 - delta*get_d(j))*data[ind]

                com_edges[c_j] += data[ind]

            # Move to the best community
            if neighbor_coms:
                best_match, val = max(((k, j) for k, j in 
                                      neighbor_coms.iteritems()),
                                      key=itemgetter(1)) # Avoid this by making heap?
                if val > neighbor_coms[c_i]:
                    C.move(i, best_match, k[i])
                    d = min(get_d(j) for j in C.get_neighbors_not_i(i)) + 1 #Can we avoid this?
                    C.set_d(i, d)
                    intra_com[i] = com_edges[best_match]

                    if offensive and num_iter > 1:
                        C.set_p(i, sum((get_p(j)/k[j] for j in
                                C.get_nodes(best_match) if j in indices)))
                    else:
                        # intra com is wrong 
                        C.set_p(i, sum(get_p(j)/intra_com[j] for j in
                                C.get_nodes(best_match) if j in indices))
                    num_moves += 1
        num_iter += 1
        delta = float(num_moves) / n
        if delta >= 0.5:
            delta = 0.0

def bdpa(A, m, n, k, C):
    t = time.time() 
    dalpa(A, m, n, k, C, False)
    
    coms = C.get_communities_renamed()
    for c in coms:  # Communites are named 0, ... n_c - 1
        p_list = [C.get_p(j) for j in coms[c]]
        ms = np.median(p_list)
        # m[c] = fns.kth_largest(p_list, (len(p_list)/2) + 1)
        for i in coms[c]:
            if C.get_p(i) <= ms:
                C.move(i, -1, k[i]) # -1 specifies the move to it's own community
                C.set_d(i, 0)
                C.set_p(i, 0)
    dalpa(A, m, n, k, C, True)
    print 'it took: ', time.time() - t
    # print modularity.modularity(A, k, m, C)
