import numpy as np 
import louvain as louvain 
from matexport import Matwriter
from visexport import Viswriter
from csdexport import Csdwriter
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
    elif ending == '.gz' or ending == '.txt':
        filename = os.path.splitext(filename)[0]
        import networkx as nx
        A = nx.to_scipy_sparse_matrix(nx.read_weighted_edgelist(filepath, delimiter =' '))  
        # A = nx.to_scipy_sparse_matrix(nx.read_adjlist(filepath))  
    else:
        print "this file extension is not recognized."
        return
    
    
    n = A.shape[1]
    k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]
    m = 0.5*A.sum()
    
    filewriter = Matwriter(filename) if args.output else None
    cytowriter = Viswriter(filename, args.vizualize[0], args.vizualize[1], args.vizualize[2]) if args.vizualize else None

    analyzer = Csdwriter(filename) if args.csd else None

    tsh = args.treshold if args.treshold else 0.02
    verbose = args.verbose if args.verbose else False
    dump = args.dump if args.dump else False

    if verbose:
        print 'File loaded. %d nodes in the network and total weight is %.2f ' % (n, m)
    
    louvain.louvain(A, m, n, k, filewriter, cytowriter, analyzer, tsh, verbose, dump)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_file", help="Specify the path of the data set")
    parser.add_argument("-t", "--treshold", help="Specify an modularity treshold used in the first phase. Default is 0.002", type=float)
    parser.add_argument("-v", "--verbose", help="Turn verbosity on", action="store_true")
    parser.add_argument("-o", "--output", help="Output to .mat file in ./results/", action="store_true")
    parser.add_argument("-d", "--dump", help="Dump communities into pickle file", action="store_true")
    parser.add_argument("-a", "--csd", help="Output component sizes", action="store_true")
    parser.add_argument("-viz", "--vizualize", nargs='+', help="Export communitiy structure to vizualize with e.g. gephi. \
        arg[0] which pass that should be the vertices \
        arg[1] the pass that indicates the community structure. \
        You need to know a priori how many passes there is.", type=int)
    args = parser.parse_args()

    if os.path.isfile(args.path_to_file):
            initialize(args.path_to_file, args)
    else:
        print "Please provide a valid file"
