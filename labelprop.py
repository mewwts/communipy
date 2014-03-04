from labels import Labels
from louvain import second_phase
import modularity
import functions as fns
import numpy as np
import sys
from collections import defaultdict
import numpy as np

def dpa(A, m, n, k):
    
    # Run defensive dalpa on the network    
    C = Labels(xrange(n), k)
    dalpa(A, m, n, k, C, False)
    print "we are in dpa, numcoms: ", len(C.get_communities_renamed())
    

    # Construct community network, and run offensive dalpa
    B = second_phase(A, C.get_communities_renamed())
    bn = B.shape[1]
    bk = [float(B.data[B.indptr[j]:B.indptr[j+1]].sum()) for j in xrange(bn)]
    BC = Labels(xrange(bn), bk)
    dalpa(B, m, bn, bk, BC, True)
    
    print "processed community network, numcoms ", len(BC.get_communities_renamed())
    newcoms = None
    if len(BC.get_communities()) == 1:
         print 'continuing with bdpa'
         bdpa(A, m, n, k, C)
    else:

        # extracting the largest community in terms of nodes from PASS 0
         if len(BC.get_communities_renamed) == bn:
            largest = C.get_largest_community()[0]
            #Anodes =
    #     
        
    #     # Bnodes are the comunities from C.renamed
        
    #     Anodes = C.get_nodes(largest)

    #     # isolate the vertices
    #     C.delete_community(largest, k) 
        
    #     D = A[Anodes,:][:, Anodes]
    #     dm = 0.5 * D.sum()
    #     dn = D.shape[1]
    #     dk = [float(D.data[D.indptr[j]:D.indptr[j+1]].sum()) for j in xrange(dn)]
    #     newcoms = dpa(D, dm, dn, dk)[0]

    # communities = C.get_communities_renamed()
    if newcoms is not None:
        for com, nodes in newcoms.iteritems():
            orgnodes = Anodes[nodes]
            C.insert_community(orgnodes, k[orgnodes])
    
    communities = C.get_communities_renamed()
    
    return communities, modularity.modularity(A, k, m, C)

def dalpa(A, m, n, k, C, offensive=False):
    """
    Defensive/Offensive label propagation. 

    """

    # function references
    get_com = C.get_community
    get_p = C.get_p
    get_d = C.get_d
    get_internal = C.get_internal

    # initialize some variables
    delta = 0.0
    num_iter = 1
    num_moves = 1
    num_checked = 0
    # while not convergence
    while num_moves > 0:
        num_moves = 0
        num_checked = 0
        for i in fns.yield_random_modulo(n):
            num_checked += 1
            print num_checked

            c_i = get_com(i)
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]

            neighbor_coms = defaultdict(int)
            max_neighbor = (-1, -1.0)
            com_edges = defaultdict(int)
            d_dict = defaultdict(lambda: sys.maxint)

            for ind, j in enumerate(indices):
                c_j = get_com(j)

                if i == j:
                    continue

                d = get_d(j)
                if d < d_dict[c_j]:
                    d_dict[c_j] = d

                if not offensive:
                    neighbor_coms[c_j] += get_p(j)*(1 - delta*d)*data[ind]
                else:
                    neighbor_coms[c_j] += (1 - get_p(j))*(1 - delta*d)*data[ind]

                if neighbor_coms[c_j] > max_neighbor[1]:
                    max_neighbor = (c_j, neighbor_coms[c_j])

                com_edges[c_j] += data[ind]

            # Move to the best community
            best_match, best_val = max_neighbor
            if best_match != c_i and best_val > neighbor_coms[c_i]:

                C.move(i, best_match, k[i], com_edges[best_match])
                C.set_d(i, d_dict[best_match] + 1)

                if offensive and num_iter > 1:
                    C.set_p(i, sum((get_p(j)/k[j] for j in
                            C.get_nodes(best_match) if j in set(indices))))
                else:
                    C.set_p(i, sum(get_p(j)/get_internal(j) for j in
                            C.get_nodes(best_match) if j in set(indices)))
                num_moves += 1

        num_iter += 1
        delta = float(num_moves) / n
        if delta >= 0.5:
            delta = 0.0

def bdpa(A, m, n, k, C):
    dalpa(A, m, n, k, C, False)
    coms = C.get_communities_renamed()
    for c in coms:
        p_list = [C.get_p(j) for j in coms[c]]
        ms = np.median(p_list)
        # m[c] = fns.kth_largest(p_list, (len(p_list)/2) + 1)
        for i in coms[c]:
            if C.get_p(i) <= ms:
                C.move(i, -1, k[i])
                C.set_d(i, 0)
                C.set_p(i, 0)
    dalpa(A, m, n, k, C, True)
