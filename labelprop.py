import copy
from labels import Labels
from community_detection import community_network
import modularity
import functions as fns
import numpy as np
import sys
from collections import defaultdict
from utils import Graph
import numexpr as nr

def propagate(G, args):
    A, m, n, k = G
    C = dpa(G, args)   
    coms = C.dict_renamed
    new_mat = community_network(A, coms)
    new_k = np.array(new_mat.sum(axis=1), 
                     dtype=float).reshape(-1,).tolist()    

    print("Found {} communities".format(len(C.dict_renamed)))
    print("Modularity of {}".format(
                modularity.diagonal_modularity(
                    new_mat.diagonal(), new_k, 0.5*new_mat.sum())))
    if args.exporter:
        args.exporter.write_nodelist(C.dict_renamed)
        args.exporter.close()
        print('Community structure outputted to .txt-file')

def dpa(G, args):
    """ Diffusion and propagation algorithm """
    ddC = Labels(xrange(G.n), G.k)
    dalpa(G, ddC, False)
    ddQ = modularity.modularity(G.A, G.k, G.m, ddC)

    if args.verbose:
        print("DDALPA found {} communities".format(len(ddC)))

    if len(ddC) != 1:
        # node in community network ---> community in ddC (A)
        mpng = {lv2_node: com for com, lv2_node in enumerate(sorted(ddC.communities.keys()))}
        # community in ddC (A) ---> node in community network
        mpng_inv = {com: lv2_node for com, lv2_node in enumerate(sorted(ddC.communities.keys()))}
            
        A_C = community_network(G.A, ddC.dict_renamed)
        G_C = Graph(A_C, 
                    G.m, 
                    A_C.shape[1], 
                    np.array(A_C.sum(axis=1), dtype=float).reshape(-1,).tolist()
                    )
        odC = Labels(xrange(G_C.n), G_C.k)
        dalpa(G_C, odC, True)
        odalpaQ = modularity.modularity(G_C.A, G_C.k, G_C.m, odC)

        if args.verbose:
            print("ODALPA on community network revealed {} communities".format(len(odC)))

        if odalpaQ >= ddQ: #and len(odC) != 1:
            # We wish to regroup the nodes into the partitioning determined
            # by offensive dalpa on the community network.
            
            n2c_mpng = [0] * G.n
            for o_c, o_nodes in odC:
                # community in community network, 
                # nodes(communities in the original network) of this community
                for o_node in o_nodes:
                    # for each of these communities(nodes)
                    for node in ddC.communities[mpng_inv[o_node]]:
                        #map every node in the community o_node to o_c
                        n2c_mpng[node] = o_c

            ddC = Labels(n2c_mpng, G.k)
            ddQ = odalpaQ
    else:
        # This is a dummy, so that we can jump into the next if 
        # that takes us to bdpa!
        odC = [0]

    if len(odC) == 1:
        # Starting over, really.
        ddC = Labels(xrange(G.n), G.k)
        bdpa(G, ddC)
    else:
        print("We are recursing")

        largest_subset = list(ddC[ddC.largest[0]])
        largest_subset.sort()
        node_mpng = {i: j for i, j in enumerate(largest_subset)}
        
        A_slice = G.A[largest_subset, :][:, largest_subset] # This is probably costly

        dk = np.array(A_slice.sum(axis=1), dtype=float).reshape(-1, ).tolist()
        H = Graph(A_slice, A_slice.sum()*0.5, A_slice.shape[1], dk)
        D = dpa(H, args)

        C = copy.deepcopy(ddC)
        for com, nodes in D:
            C.insert_community([node_mpng[node] for node in nodes], G.k)
        new_mod = modularity.modularity(G.A, G.k, G.m, C)
        if  new_mod > ddQ:
            ddC = C

    return ddC

def dalpa(G, C, offensive=False):
    """
    Defensive/Offensive label propagation. 

    """
    A, m, n, k = G
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
                print A.indices
                print A.data
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

def bdpa_modified(G, C):
    coms = C.dict_renamed
    for c, nodes in coms.iteritems():
        p_list = [C.p[j] for j in nodes]
        for i in C[c].copy():
            if C.p[i] <= np.median(p_list):
                C.move(i, -1, G.k[i])
                C.d[i] = 0
                C.p[i] = 0
    dalpa(G, C, True)

def bdpa(G, C):
    dalpa(G, C, False)
    bdpa_modified(G, C)
