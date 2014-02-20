import argparse
import numpy as np
import os
import random
from scipy import io, sparse
import time

def erdos_renyi(n1, n2, p1, p2):
    random.seed(time.time())
    coos = set([])

    def add(i, j):
        coos.add((i, j))
        coos.add((j, i))

    for i in xrange(n1):
        for j in xrange(i, n1):
            if random.random() < p1:
                add(i, j)

    for i in xrange(n1,n1+n2):
        for j in xrange(n1+n2):
            if j < n1 and random.random() < p2:
                add(i, j)
            elif j >= n1:
                add(i, j)

    A = sparse.coo_matrix(([1 for i in xrange(len(coos))], zip(*coos))).tocsr()
    ncomp, labels = sparse.csgraph.connected_components(A, directed=False)

    if ncomp > 1:
        print "Graph was initially not connected. Returning the largest \
               connected component"
        max_label = max(((count, i) for i, count in
                        enumerate(np.bincount(labels))))[1]
        
        A = A[labels == max_label, :][:, labels == max_label]

    return A

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_output",
        help="Specify where to save output")
    parser.add_argument("sizes", nargs=2, \
        help="Specify the size of the random graph and the embedded \
        complete graph.", type = int)
    parser.add_argument("-p", "--prob", nargs=2, \
        help="Specify the probability of connecting the nodes in the \
        random graph with each other, and the probability of \
        connecting a node in the complete graph with the random one.", \
        type = float)
    args = parser.parse_args()
    path = args.path_to_output
    if os.path.isdir(os.path.dirname(path)):
        A = erdos_renyi(args.sizes[0], args.sizes[1],
                        args.prob[0], args.prob[1]) 
        io.savemat(path, {'mat': A}, do_compression=True, oned_as='row')
    else:
        print "Please provide a valid file destination"

if __name__ == '__main__':
    main()
