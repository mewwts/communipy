import argparse
from collections import defaultdict
import numpy as np
from scipy import sparse
from math import log

def parse(path):
    return np.loadtxt(path, dtype=int)[:, -1]

def log2(x): 
    return log(x, 2)

def mutual_information(N):
    hxy = joint_entropy(N)
    h_known = entropy(N.sum(axis=1)) # row sums
    h_found = entropy(N.sum(axis=0)) # col sums
    return h_known + h_found - hxy

def joint_entropy(N):
    H = 0
    for (i,j) in zip(*N.nonzero()):
        nij = N[i,j]
        H += -1 * nij * log2(nij)
    return H

def entropy(n):
    H = 0
    for e in n:
        if e !=0:
            H += -1 * e * log2(e)
    return H

def variation_of_information(N):
    hxy = joint_entropy(N)
    ixy = mutual_information(N)
    return hxy - ixy

def normalized_variation_of_information(N):
    hxy = joint_entropy(N)
    ixy = mutual_information(N)
    return 1 - (ixy/hxy)

def normalized_mutual_information(N):
    ixy = mutual_information(N)
    h_known = entropy(N.sum(axis=1))
    h_found = entropy(N.sum(axis=0))
    return 2*ixy/(h_known + h_found)

def max_mutual_information(N):
    ixy = mutual_information(N)
    h_known = entropy(N.sum(axis=1))
    h_found = entropy(N.sum(axis=0))
    return ixy/max((h_known,h_found))

def joint_density(found, known):

        # found -= 1
    
    n_found = len(np.unique(found))
    n_known = len(np.unique(known))
    print("{} x {} density".format(n_found, n_known))

    # coo-matrix will sum duplicate entries
    confusion = np.asarray(
        sparse.coo_matrix(
            (np.ones(known.shape[0], dtype=float), (known, found)),
            shape=(n_known, n_found)
        ).todense()
    )
    print confusion
    return confusion/confusion.sum(dtype=float)

def test(found, known):
    fdict = defaultdict(set)
    kdict = defaultdict(set)
    for i, c in enumerate(found):
        fdict[c].add(i)
    for i, c in enumerate(known):
        kdict[c].add(i)

    for i in fdict.keys():
        for j in kdict.keys():
            if fdict[i] == kdict[j]:
                print("Found a match")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("found")
    parser.add_argument("known")
    parser.add_argument("--ext", action="store_true",
                        help="Put this if nodes are number from 1.")
    args = parser.parse_args()
    
    if not (args.found and args.known):
        print("Please specify both files")
        return

    found = parse(args.found)
    known = parse(args.known)

    if args.ext:
        known -= 1    
    N = joint_density(found, known)
    # print(N)
    print("---Testing {} vs. {}---".format(args.found, args.known))
    print("Variation of information (VI): {}".format(variation_of_information(N)))
    print("Normalized VI: {}".format(normalized_variation_of_information(N)))
    print("Mutual Information (MI): {}".format(mutual_information(N)))
    print("Normalized MI: {}".format(normalized_mutual_information(N)))
    print("Max-normalized MI: {} \n".format(max_mutual_information(N)))

if __name__ == '__main__':
    main()