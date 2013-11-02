import time 
import numpy as np 
import louvain as louvain 
from output import Matwriter
import argparse
from scipy import sparse
import os



def initialize(filepath, args):
    
    filename, ending = os.path.splitext(filepath)
    if ending == '.mat':
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
    
    filewriter = Matwriter(filename) if args.output else None

    tsh = args.treshold if args.treshold else 0.02
    verbose = args.verbose if args.verbose else False
    dump = args.dump if args.dump else False
    
    t = time.time()
    louvain.louvain(A, m, n, k, filewriter, tsh, verbose, dump)
    print "It took %s seconds" % (time.time() - t)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_file", help="Specify the path of the data set")
    parser.add_argument("-t", "--treshold", help="Specify an modularity treshold used in the first phase. Default is 0.002", type=float)
    parser.add_argument("-v", "--verbose", help="Turn verbosity on", action="store_true")
    parser.add_argument("-o", "--output", help="Output too file in ./results/", action="store_true")
    parser.add_argument("-d", "--dump", help="Dump communities", action="store_true")
    args = parser.parse_args()
    if os.path.isfile(args.path_to_file):
            initialize(args.path_to_file, args)
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
