import time 
import numpy as np 
from scipy import sparse, io
import louvain as louvain 
import networkx as nx 
from output import Matwriter



def main():
    #filename = '../Data/example.csv'
    #filename = '../Data/karate.gml'
    #filename = '../Data/lesmis.gml'
    #filename = '../Data/netscience.gml'
    #filename = '../Data/internet.dat.gz'
    #filename = '../Data/cond-mat-2003.gml'
    #filename = '../Data/dolphins.mat'
    #filename = '../Data/as-22july06.gml'
    #filename = '../Data/polbooks.gml'
    filename = "../Data/MAT_MIN_20111221_sym.mat" 
    #A = io.loadmat(filename)['Problem'][0][0][2].tocsr()
    #A = sparse.csr_matrix(np.genfromtxt(filename, delimiter=',')) # from the articel
    A = sparse.csr_matrix(io.loadmat(filename)['mat'])
    #A = nx.to_scipy_sparse_matrix(nx.read_adjlist(filename))
    #A = nx.to_scipy_sparse_matrix(nx.read_gml(filename)) #gmls
    n = A.shape[1]
    k = [float(A.data[A.indptr[j]:A.indptr[j+1]].sum()) for j in xrange(n)]
    #k = np.array(A.sum(1)).reshape(n) # the degree sequence
    m = 0.5*A.sum() # the number of edges/the total weight
    filewriter = Matwriter(filename)
    t = time.time()
    louvain.louvain(A, m, n, k, filewriter)
    print "It took %s seconds" % (time.time() - t)

if __name__ == '__main__':
    main()
