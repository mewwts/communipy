from __future__ import division
from operator import itemgetter
from collections import defaultdict
import functions as fns
import modularity
import copy
import numpy as np
from labels import Labels
from utils import Graph
from community_detection import community_network
MAX_ITER = 100

def propagate(G, args):
    G.A.data = np.repeat(1, G.A.data.shape[0])
    k = np.array(G.A.sum(axis=1), dtype=float).reshape(-1,).tolist()
    G = Graph(G.A, len(G.A.data) / 2, G.n, k)
    C = dpa(G, args)
    print("Found {} communities".format(len(C.dict_renamed)))
    print("Modularity = {}".format(modularity.modularity(G, C)))
    if args.exporter:
        args.exporter.write_nodelist(C.dict_renamed)
        args.exporter.close()
        print('Community structure outputted to .txt-file')

def dalpa(G, C, offensive=False):
    """
    Defensive and offensive diffusion and label propagation algorithm.

    Propagates labels along the graph until an equilibrium is reached. 

    """
    print("Running Dalpa. Offensive={}".format(offensive))
    global MAX_ITER
    A, m, n, k = G
    num_iter = 0
    delta = 0.0
    while num_iter < MAX_ITER:
        num_moves = 0

        for i in fns.yield_random_modulo(G.n):
            indices = A.indices[A.indptr[i]:A.indptr[i+1]]
            scores = defaultdict(float)
            for j in indices:
                if j != i:
                    if not offensive:
                        first_term = C.p[j]
                    else:
                        first_term = (1 - C.p[j])
                    scores[C.nodes[j]] += first_term * (1.0 - delta * C.d[j])

            old = C.nodes[i]

            if scores:
                
                new = max(scores.iteritems(), key=itemgetter(1))[0]

                if scores[old] < scores[new]:
                    C.move(i, new, k[i])

                    dist = n * 10
                    C.p[i] = 0.0
                    C.internal[i] = 0

                    
                    for v in A.indices[A.indptr[i]:A.indptr[i+1]]:
                        if v != i:
                            if C.nodes[v] == new:
                                if C.d[v] < dist:
                                    dist = C.d[v]
                                C.internal[i] += 1
                                C.internal[v] += 1
                                if not offensive:
                                    C.p[i] += C.p[v] / C.internal[v]
                                else:
                                    C.p[i] += C.p[v] / k[v]

                            elif C.nodes[v] == old:
                                C.internal[v] -= 1

                    C.d[i] = dist + 1
                    num_moves += 1
        
        ratio = num_moves / n
        if ratio < 0.5 and num_iter > 0:
            delta = ratio
        else:
            delta = 0.0

        num_iter += 1
        print num_moves
        if num_moves == 0:
            break

    if num_iter >= MAX_ITER:
        print "reached max iter"
    print "found {} communities".format(len(C))

def dpa(G, args):
    """
    Diffusion and propagation algorithm. 
    
    """
    # Run defensive dalpa
    defensive_C = Labels(xrange(G.n), G.k, G.A.diagonal())
    dalpa(G, defensive_C, offensive=False)
    defensive_Q = modularity.modularity(G, defensive_C)

    # Construct the community network
    A_C = community_network(G.A, defensive_C.dict_renamed)
    G_C = Graph(A_C, 
                G.m,
                A_C.shape[1], 
                np.array(A_C.sum(axis=1), dtype=float).reshape(-1,).tolist()
                )

    # Run offensive dalpa on the community network
    offensive_C = Labels(xrange(G_C.n), G_C.k, G_C.A.diagonal())
    dalpa(G_C, offensive_C, offensive=True)
    offensive_Q = modularity.modularity(G_C, offensive_C)

    # if the modularity of the offensive run is higher than the modularity
    # of the defensive run, we wish to transfer the labels/communities of
    # community network onto the real network. 

    if offensive_Q > defensive_Q and len(offensive_C) > 1:
        clustering = [-1] * G.n
        # community in G_C holds communities in G
        for high_level_c, low_level_cs in offensive_C:
            for low_level_c in low_level_cs:
                for node in defensive_C[low_level_c]:
                    clustering[node] = high_level_c
     
        # Keep in mind that the internal edges are wrong below
        defensive_C = Labels(clustering, G.k, G.A.diagonal())
        defensive_Q = offensive_Q

        # # If we need to fix the intra-community edges:
        # defensive_C.internal = [0] * G.n
        # for c, nodes in defensive_C:
        #     for u in nodes:
        #         for v in G.A.indices[G.A.indptr[u]:G.A.indptr[u+1]]:
        #             if v != u:
        #                 if defensive_C.nodes[v] == c:
        #                     defensive_C.internal[u] += 1
    
    if len(offensive_C) == 1:
        defensive_C = Labels(xrange(G.n), G.k, G.A.diagonal())
        defensive_C = bdpa(G, defensive_C)
        return defensive_C
    else:
        print "RECURSING"
        # print defensive_C.dict
        largest = list(defensive_C[defensive_C.largest])
        largest.sort()

        # mapping vertex in subset-graph to vertex in real graph
        mapping = {i: j for i, j in enumerate(largest)}

        A_subset = G.A[largest, :][:, largest]
        G_subset = Graph(
            A_subset,
            A_subset.sum() / 2,
            A_subset.shape[1],
            np.array(A_subset.sum(axis=1), dtype=float).reshape(-1, ).tolist()
            )
        recursive_C = dpa(G_subset, args)
        new_C = copy.deepcopy(defensive_C)

        for c, nodes in recursive_C:
            new_C.insert_community([mapping[node] for node in nodes], G.k)

        new_Q = modularity.modularity(G, new_C)

        if new_Q > defensive_Q:
            defensive_C = new_C

        return new_C

def bdpa(G, C):
    print "Running BDPA"
    dalpa(G, C, offensive=False)
    defensive_Q = modularity.modularity(G, C)
    print "defensive_Q = {} ".format(defensive_Q)
    new_C = copy.deepcopy(C)
    for c, nodes in C:
        median = np.median([C.p[j] for j in nodes])
        for i in C[c]:
            if new_C.p[i] <= median:
                new_C.move(i, -1, G.k[i])
                new_C.d[i] = 0
                new_C.p[i] = 0
                new_C.internal[i] = G.A[i,i]
    # Fix internal edges
    new_C.internal = [0] * G.n
    for i in xrange(G.n):
        for j in G.A.indices[G.A.indptr[i]:G.A.indptr[i+1]]:
            if new_C.nodes[i] == new_C.nodes[j]:
                new_C.internal[i] += 1
    dalpa(G, new_C, True)
    offensive_Q = modularity.modularity(G, new_C)
    print "offensive_Q = {} ".format(offensive_Q)
    if offensive_Q > defensive_Q:
        return new_C
    else:
        return C



