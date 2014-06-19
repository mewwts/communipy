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
from utils import Graph

def initialize(A, filepath, args):
    """
    Set up a Graph (named tuple) and instantiate some objects based on 
    the arguments passed to the program, then run the algorithm 
    specified by args.method.

    Args:
    A: A symmetric SciPy CSR-matrix
    filepath: Path to the file from which A was loaded
    args: All the arguments provided to the program

    """
    filename, ending = os.path.splitext(filepath)

    k = np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist()
    m = 0.5*A.sum()
    n = A.shape[0]
    G = Graph(A, m, n, k)

    prop = True if args.prop else False
    exporter = Exporter(filename, G.n, prop) if args.output else None
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
    elif args.rank:
        method =  Method.rank
    elif args.dissolve:
        method = Method.dissolve
    else:
        method = Method.luv

    arguments = Arguments(exporter, cytowriter, analyzer, 
                          tsh, verbose, dump, method)

    if arguments.verbose:
        print("File loaded. {} nodes in the network and total weight "
              "is {}".format(G.n, G.m))
    if arguments.method == Method.prop:
        labelprop.propagate(G, arguments)
    else:
        community_detect(G, arguments)

def get_graph(filepath):
    """
    Load the matrix saved at filepath.

    Args:
    filepath: path to file holding a sparse matrix

    Returns:
    A: SciPy CSR matrix

    """
    filename, ending = os.path.splitext(filepath)
    if ending == '.mat':
        from scipy import io
        A = sparse.csr_matrix(io.loadmat(filepath)['mat'], dtype=float)
    elif ending == '.csv':
        A = sparse.csr_matrix(np.genfromtxt(filepath, delimiter=','), 
                              dtype=float)
    elif ending == '.gml':
        import networkx as nx 
        A = nx.to_scipy_sparse_matrix(nx.read_gml(filepath), dtype=float)
    elif ending == '.dat':
        adjlist = np.genfromtxt(filepath)
        
        if adjlist.shape[1] == 2:
            data = np.ones(adjlist.shape[0])
            if np.min(adjlist) == 1:
                adjlist -= 1 # 0 indexing
        else:
            data = adjlist[:, 2]
            if np.min(adjlist[:, :-1]) == 1:
                adjlist[:, :-1] -= 1 # 0 indexing
        A = sparse.coo_matrix((data, 
                              (np.array(adjlist[:,0], dtype=int),
                              np.array(adjlist[:,1], dtype=int))),
                              dtype=float).tocsr()            

    elif ending == '.gz' or ending == '.txt':
        filename = os.path.splitext(filename)[0]
        import networkx as nx
        A = nx.to_scipy_sparse_matrix(
                nx.read_weighted_edgelist(filepath, delimiter =' '),
                dtype=float)  
    else:
        raise IOError("Could not parse file")
    return A

def main():
    """
    Parses all arguments passed in the command line and loaded the graph
    located at args.path_to_file. Calls initialize if all arguments
    are valid

    """
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