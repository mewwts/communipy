import time 
import numpy as np 
from scipy import sparse, io
import louvain as louvain 
import networkx as nx 

def main():
    
    # initialise variables
    #A = sparse.csr_matrix(np.genfromtxt('../Data/example.csv', delimiter=',')) # from the articel
    #A = sparse.csr_matrix(io.loadmat("../Data/MAT_MIN_20111221.mat")['mat'])
    
    #A = nx.to_scipy_sparse_matrix(nx.read_gml('../Data/karate.gml')) #Karate
    #A = nx.to_scipy_sparse_matrix(nx.read_gml('../Data/as-22july06.gml')) #Internet NB: huge
    #A = nx.to_scipy_sparse_matrix(nx.read_gml('../Data/polbooks.gml')) #Political books
    A = nx.to_scipy_sparse_matrix(nx.read_gml('../Data/lesmis.gml')) #les miserables
    n = A.shape[1]
    k = np.array(A.sum(1)).reshape(n) # the degree sequence
    m = 0.5*A.sum() # the number of edges
    t = time.time()
    louvain.louvain(A, m, n, k)
    print "It took %s seconds" % (time.time() - t)

if __name__ == '__main__':
    main()