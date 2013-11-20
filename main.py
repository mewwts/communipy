
import numpy as np 
import louvain as louvain 
from output import Matwriter
from cytowriter import Cytowriter
from analyzer import Analyzer
import argparse
from scipy import sparse
import os



def initialize(filepath, args):
    
    filename, ending = os.path.splitext(filepath)
    if ending == '.mat':
        from scipy import io
        A = sparse.csr_matrix(io.loadmat(filepath)['mat'])
    elif ending == '.csv':
        A = sparse.csr_matrix(np.genfromtxt(filepath, delimiter=','))
    elif ending == '.gml':
        import networkx as nx 
        A = nx.to_scipy_sparse_matrix(nx.read_gml(filepath))
    elif ending == '.gz':
        filename = os.path.splitext(filename)[0]
        import networkx as nx
        A = nx.to_scipy_sparse_matrix(nx.read_adjlist(filepath))   
    else:
        print "this file extension is not recognized."
        return
    
    
    n = A.shape[1]
    k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]
    m = 0.5*A.sum()
    
    filewriter = Matwriter(filename) if args.output else None
    cytowriter = Cytowriter(filename, args.cytoscape[0], args.cytoscape[1:]) if args.cytoscape else None

    analyzer = Analyzer(filename) if args.csd else None

    tsh = args.treshold if args.treshold else 0.02
    verbose = args.verbose if args.verbose else False
    dump = args.dump if args.dump else False

    
    louvain.louvain(A, m, n, k, filewriter, cytowriter, analyzer, tsh, verbose, dump)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_file", help="Specify the path of the data set")
    parser.add_argument("-t", "--treshold", help="Specify an modularity treshold used in the first phase. Default is 0.002", type=float)
    parser.add_argument("-v", "--verbose", help="Turn verbosity on", action="store_true")
    parser.add_argument("-o", "--output", help="Output too file in ./results/", action="store_true")
    parser.add_argument("-d", "--dump", help="Dump communities", action="store_true")
    parser.add_argument("-a", "--csd", help="Plot component size distribution when finished", action="store_true")
    parser.add_argument("-c", "--cytoscape", nargs='+', help="Export communitiy structure to use with cytoscape. \
        The number indicates the minimum number of nodes within a community to visualize it", type=int)
    args = parser.parse_args()

    if os.path.isfile(args.path_to_file):
            initialize(args.path_to_file, args)
    else:
        print "Please provide a valid file"
