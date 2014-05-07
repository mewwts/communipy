import numpy as np 
from export_communities import Exporter
from visexport import Viswriter
from csdexport import Csdwriter
import argparse
from scipy import sparse
import os
from community_detection import community_detect
from utils import Method
from utils import Arguments


def initialize(A, filepath, args):
    filename, ending = os.path.splitext(filepath)

    n = A.shape[1]
    k = np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist() 
    m = 0.5*A.sum()

    prop = True if args.prop else False
    exporter = Exporter(filename, n, prop) if args.output else None
    cytowriter = None
    if args.visualize:
        cytowriter = Viswriter(filename, args.vizualize[0],
                               args.vizualize[1], A)

    analyzer = Csdwriter(filename) if args.csd else None
    tsh = args.treshold if args.treshold else 0.02
    verbose = args.verbose if args.verbose else False
    dump = args.dump if args.dump else False
    


    if args.prop:
        import labelprop
        method = Method.prop
    if args.rank:
        method =  Method.rank
    elif args.dissolve:
        method = Method.dissolve
    else:
        method = Method.luv

    arguments = Arguments(exporter, cytowriter, analyzer, 
                          tsh, verbose, dump, method)
    
    if arguments.verbose:
        print("File loaded. {} nodes in the network and total weight"
              "is {}".format(n, m))
    if arguments.method == Method.prop:
        labelprop.propagate(A, m, n, k, arguments)
    else:
        community_detect(A, m, n, k, arguments)

def get_graph(filepath):
    filename, ending = os.path.splitext(filepath)
    if ending == '.mat':
        from scipy import io
        A = sparse.csr_matrix(io.loadmat(filepath)['mat'])
    elif ending == '.csv':
        A = sparse.csr_matrix(np.genfromtxt(filepath, delimiter=','))
    elif ending == '.gml':
        import networkx as nx 
        A = nx.to_scipy_sparse_matrix(nx.read_gml(filepath))
    elif ending == '.dat':
        adjlist = np.genfromtxt(filepath, dtype=int)
        adjlist -= 1 # 0 indexing
        A = sparse.coo_matrix((np.ones(adjlist.shape[0]), 
                    (adjlist[:,0], adjlist[:,1])), dtype=float).tocsr()

    elif ending == '.gz' or ending == '.txt':
        filename = os.path.splitext(filename)[0]
        import networkx as nx
        A = nx.to_scipy_sparse_matrix(
                nx.read_weighted_edgelist(filepath, delimiter =' '))  
    else:
        raise IOError
    return A

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_file", 
                        help="Specify the path of the data set")
    parser.add_argument("-t", "--treshold", type=float,
                        help="Specify an modularity treshold used in the \
                        first phase. Default is 0.002")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Turn verbosity on")
    parser.add_argument("-o", "--output", action="store_true",
                        help="Output community structure to .txt file"
                             "in ./results/")
    parser.add_argument("--dump", action="store_true",
                        help="Dump communities into pickle file")
    parser.add_argument("-c", "--csd", action="store_true",
                        help="Output component sizes")
    parser.add_argument("-vis", "--visualize", nargs='+', type=int,
                        help="Export communitiy structure to vizualize with \
                              e.g. gephi:\
                              arg[0] pass# that should be the vertices \
                              arg[1] pass# that indicates the community \
                              structure")
    parser.add_argument("-p", "--prop", action="store_true", 
                        help="Use labelpropagation algorithm")
    parser.add_argument("-r", "--rank", action="store_true", 
                        help="Use degree-rank algorithm")
    parser.add_argument("-d", "--dissolve", action="store_true",
                        help="Use community-dissolve algorithm")

    args = parser.parse_args()

    if os.path.isfile(args.path_to_file):
            try:
                A = get_graph(args.path_to_file)
            except IOError:
                print("This file extension is not recognized.")
                return
            initialize(A, args.path_to_file, args)
    else:
        print("Please provide a valid input file")

if __name__ == '__main__':
    main()