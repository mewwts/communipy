from labels import Labels
from louvain import second_phase
import modularity
import functions as fns
import numpy as np
import sys
from collections import defaultdict
import numexpr as nr

def propagate(A, m, n, k, args):
    C = dpa(A, m, n, k, args)   
    coms = C.dict_renamed
    new_mat = second_phase(A, coms)
    new_k = np.array(new_mat.sum(axis=1), 
                     dtype=float).reshape(-1,).tolist()    

    print(C.dict_renamed)
    print("Modularity of {}".format(
                modularity.diagonal_modularity(
                    new_mat.diagonal(), new_k, 0.5*new_mat.sum())))
    if args.exporter:
        args.exporter.write_nodelist(C.dict_renamed)
        args.exporter.close()
        print('Community structure outputted to .txt-file')

def dpa(A, m, n, k, args):
    """ Diffusion and propagation algorithm """
    D = None

    ddC = Labels(xrange(n), k)
    dalpa(A, m, n, k, ddC, False)
    ddalpaQ = modularity.modularity(A, k, m, ddC)

    if args.verbose:
        print("DDALPA found {} communities".format(len(ddC)))

    # node in A_C ---> community in ddC (A)
    mpng = {i: c for i, c in enumerate(sorted(ddC.dict.keys()))}
    
    A_C = second_phase(A, ddC.dict_renamed)
    k_C = np.array(A_C.sum(axis=1), dtype=float).reshape(-1,).tolist()
    odC = Labels(xrange(A_C.shape[1]), k_C)
    dalpa(A_C, m, A_C.shape[1], k_C, odC, True)
    odalpaQ = modularity.modularity(A_C, k_C, m, odC)

    if args.verbose:
        print("ODALPA on community network revealed {} communities".format(len(odC)))

    if odalpaQ >= ddalpaQ and len(odC) != 1:
        print "we in here!"
        # map the nodes in pass one to the communities from the community network.
        mapping = [0] * n
        for o_c, o_nodes in odC:
            for o_node in o_nodes:
                for node in ddC.communities[mpng[o_node]]:
                    mapping[node] = o_c

        ddC = Labels(mapping, k)
        ddQ = odalpaQ

    elif len(odC) == 1:
        print "flood-filled"
        # Starting over, really.
        C = Labels(xrange(n), k)
        bdpa(A, m, n, k, C)
    else:
        print("We are recursing")
        # extract the largest community in terms of nodes from PASS 0
        largest_subset = []

        # community ---> nodes in A
        inv_mpng = defaultdict(list)
        for i, c in mpng.iteritems():
            inv_mpng[c].append[i]

        for c, nodes in odC:
            size = 0
            subset = []
            for node in nodes: 
                subset.extend(inv_mpng[node])
                size += C.size(inv_mpng[node])
            if size > len(largest_subset):
                largest_subset = subset

        subset.sort()
        node_mpng = {i:j for i, j in enumerate(subset)}
        A_slice = A[subset, :][:, subset] # This is probably costly
        dk = np.array(A_slice.sum(axis=1), dtype=float).reshape(-1,).tolist()
        D = dpa(A_slice, A_slice.sum()*0.5, A_slice.shape[1], dk, args)

        C = ddC.copy()
        for com, nodes in D:
            C.insert_community([node_mpng[node] for node in nodes], dk)
        if modularity.modularity(A, k, m, C) < ddQ:
            C = ddC

    return C

def dalpa(A, m, n, k, C, offensive=False):
    """
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

            c_i = C.nodes[i]
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            data = A.data[A.indptr[i]:A.indptr[i+1]]

            neighbor_coms = defaultdict(float)
            max_neighbor = (-1, -1.0)
            com_edges = defaultdict(float)
            d_dict = defaultdict(lambda: sys.maxint)
            p_dict = defaultdict(float)
            nb_dict = {}

            for ind, j in enumerate(indices):
                aij = data[ind]
                nb_dict[j] = aij
                c_j = C.nodes[j]
                p_j = C.p[j]

                if i == j:
                    continue

                d = C.d[j]
                if d < d_dict[c_j]:
                    d_dict[c_j] = d

                if not offensive:
                    neighbor_coms[c_j] += p_j*(1 - delta*d)*aij
                    if C.internal[j] != 0:
                        p_dict[c_j] += p_j/C.internal[j]
                else:
                    neighbor_coms[c_j] += (1 - p_j)*(1 - delta*d)*aij
                    p_dict[c_j] += p_j/k[j]

                if neighbor_coms[c_j] > max_neighbor[1]:
                    max_neighbor = (c_j, neighbor_coms[c_j])

                com_edges[c_j] += aij

            # Move to the best community
            best_match, best_val = max_neighbor
            if best_match == -1:
                print("Best match = -1... ")
                print i
                print indices
                print data
                # print C.communities[C.nodes[i]]
                continue

            if best_match != c_i and best_val > neighbor_coms[c_i]:

                C.move(i, best_match, k[i], com_edges[best_match], nb_dict)
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
        for i in C[c].copy():
            if C.p[i] <= np.median(p_list):
                C.move(i, -1, k[i])
                C.d[i] = 0
                C.p[i] = 0
    dalpa(A, m, n, k, C, True)

def bdpa(A, m, n, k, C):
    dalpa(A, m, n, k, C, False)
    bdpa_modified(A, m, n, k, C)
