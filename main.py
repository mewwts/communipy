import time 
import numpy as np 
import louvain as louvain 
from output import Matwriter
import argparse
from scipy import sparse
import os



def initialize(filepath, tsh = 0.02):
    
    filename, ending = os.path.splitext(filepath)
    if ending == 'mat':
        from scipy import io
        A = sparse.csr_matrix(io.loadmat(filepath)['mat'])
        #A = io.loadmat(filepath)['Problem'][0][0][2].tocsr()
    elif ending == '.csv':
        A = sparse.csr_matrix(np.genfromtxt(filepath, delimiter=','))
    elif ending == '.gml':
        from scipy import io
        A = sparse.csr_matrix(io.loadmat(filepath)['mat'])
    elif ending == '.dat.gz':
        import networkx as nx 
        A = nx.to_scipy_sparse_matrix(nx.read_adjlist(filepath))   
    else:
        print "this file extension is not recognized."
        return

    n = A.shape[1]
    k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]
    m = 0.5*A.sum()
    filewriter = Matwriter(filename)
    t = time.time()
    louvain.louvain(A, m, n, k, filewriter, tsh)
    print "It took %s seconds" % (time.time() - t)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_file", help="Specify the path of the data set")
    parser.add_argument("--treshold", help="Specify an modularity treshold used in the first phase. Default is 0.002", type=float)
    parser.add_argument("-v", "--verbose", help="Turn verbosity on or off", action="store_true")
    args = parser.parse_args()
    if os.path.isfile(args.path_to_file):
        if args.treshold:
            initialize(args.path_to_file, args.treshold)
        else:
            initialize(args.path_to_file)
    else:
        print "Please provide a valid file"

    #filename = '../Data/example.csv'
    #filename = '../Data/karate.gml'
    #filename = '../Data/lesmis.gml'
    #filename = '../Data/netscience.gml'
    #filename = '../Data/internet.dat.gz'
    #filename = '../Data/cond-mat-2003.gml'
    #filename = '../Data/dolphins.mat'
    #filename = '../Data/as-22july06.gml'
    #filename = '../Data/polbooks.gml'
    #filename = "../Data/MAT_MIN_20111221_sym.mat" 
    #filename = "../Data/MAT_MIN_sym.mat" 
