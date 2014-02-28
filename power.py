import argparse
import os
import numpy as np
from scipy import io, sparse
import main

def power(mtx, exp, path=None):
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

    data = np.array(A[nz[0], nz[1]], dtype=float)[0]

    Ak = sparse.csr_matrix((data, indices, indptr))

    if path:
        io.savemat(path, {'mat': Ak}, do_compression=True, oned_as='row')
    return Ak

def power_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_input", \
        help="Specify the path of the input data set")
    parser.add_argument("power", type=int, \
        help="Specify to which power to raise the matrix to")
    parser.add_argument("path_to_output", \
        help="Specify where to save output")
    args = parser.parse_args()
    in_path = args.path_to_input
    out_path = args.path_to_output

    if os.path.isfile(in_path) and os.path.isdir(os.path.dirname(in_path)):
        filename, ending = os.path.splitext(in_path)
        try:
            A = main.get_graph(in_path)
        except IOError:
            print "File format not recognized"
        else:
            power(A, args.power, out_path) 
    else:
        print "Specify a valid parameters"


if __name__ ==  '__main__':
    power_main()