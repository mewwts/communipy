import argparse
import numpy as np
from scipy import sparse
from math import log

def parse(path):
    return np.loadtxt(path, dtype=int)[:, -1]

def log2(x): 
        if x == 0:
            return 0.0
        return log(x, 2)

def mutual_information(N):
    hxy = joint_entropy(N)
    hx = entropy(N, 1) # rows
    hy = entropy(N, 0) # cols

    return hx + hy - hxy


def joint_entropy(N):
    H = 0
    for (i,j) in zip(*N.nonzero()):
        nij = N[i,j]
        H += -1 * nij * log2(nij)
    return H

def entropy(N, ax=0):
    n = N.sum(axis=ax)
    H = 0
    for i in n:
        if i !=0:
            H += -1 * i * log2(i)
    return H

def variation_of_information(N):
    hxy = joint_entropy(N)
    ixy = mutual_information(N)
    return hxy - ixy

def normalized_mutual_information(N):
    hxy = joint_entropy(N)
    hx = entropy(N, 1)
    hy = entropy(N, 0)

    return 2*hxy/(hx + hy) # symmetric uncertainty

def init(foundpath, knownpath, external=False):
    found = parse(foundpath)
    known = parse(knownpath)
    if external:
        known -= 1
        found -= 1
    
    n_found = len(np.unique(found))
    n_known = len(np.unique(known))
    confusion = np.asarray(
        sparse.coo_matrix(
            (np.ones(known.shape[0], dtype=float), (known, found)),
            shape=(n_known, n_found)
        ).todense()
    )
    return confusion/confusion.sum(dtype=float)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("found")
    parser.add_argument("known")
    parser.add_argument("--ext", action="store_true")
    args = parser.parse_args()
    
    if not (args.found and args.known):
        print("Please specify both files")
        return
    N = init(args.found, args.known, args.ext)
    print N
    # print NMI(N)
    print normalized_mutual_information(N)

if __name__ == '__main__':
    main()