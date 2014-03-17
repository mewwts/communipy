import argparse
import os
import numpy as np
from scipy import io, sparse
from scipy.sparse import linalg
import main

def power(mtx, exp):
    # This is not very efficient.
    indptr = mtx.indptr
    indices = mtx.indices
    nz = mtx.nonzero()
    # A = mtx.tolil()
    I = sparse.identity(mtx.shape[1], dtype=float, format='csr')
    # A.setdiag([1 for i in xrange(A.shape[1])])
    A = mtx + I
    for i in xrange(int(exp)-1):
        A = A.dot(A)
    # Ak = A

    data = np.array(A[nz[0], nz[1]], dtype=float)[0]

    Ak = sparse.csr_matrix((data, indices, indptr))
    return Ak

def walk_generator(A):
    I = sparse.identity(A.shape[1], dtype=float)
    inv_mat = linalg.inv((I-A).tocsc()).tocsr()
    return inv_mat

def exponentiate(A):
    exp_mat = linalg.expm(A.tocsc()).tocsr()
    return exp_mat

def power_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_input",
                        help="Specify the path of the input data set")
    parser.add_argument("-p", "--power", type=int,
                        help="Specify to which power to raise the matrix to")
    parser.add_argument("-w", "--walk", help="Calculate (I-A)^-1",
                        action="store_true")
    parser.add_argument("-e", "--exp", help="Calculate exp(A)",
                        action="store_true")
    parser.add_argument("path_to_output", \
        help="Specify where to save output")
    args = parser.parse_args()
    in_path = args.path_to_input
    out_path = args.path_to_output
    if os.path.isfile(in_path):
        filename, ending = os.path.splitext(in_path)
        out_path, out_ending = os.path.splitext(out_path)
        try:
            A = main.get_graph(in_path)
        except IOError:
            print("File format not recognized")
        else:
            if args.power:
                mat = power(A, args.power)
            elif args.walk:
                mat = walk_generator(A)
            elif args.exp:
                mat = exponentiate(A)
            else:
                print("No valid arguments, see -h")
            if out_path:
                io.savemat(out_path, {'mat': mat}, do_compression=True, oned_as='row')
    else:
        print("Specify a valid parameters")


if __name__ ==  '__main__':
    power_main()