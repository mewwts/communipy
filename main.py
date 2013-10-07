import time 
import numpy as np 
from scipy import sparse, io
import louvain as louvain 
import networkx as nx 
from output import Matwriter
import os

def main():
    #filename = '../Data/example.csv'
    #filename = '../Data/karate.gml'
    #filename = '../Data/lesmis.gml'
    #filename = '../Data/as-22july06.gml'
    filename = '../Data/polbooks.gml'

    #A = sparse.csr_matrix(np.genfromtxt(filename, delimiter=',')) # from the articel
    #A = sparse.csr_matrix(io.loadmat("../Data/MAT_MIN_20111221.mat")['mat'])
    A = nx.to_scipy_sparse_matrix(nx.read_gml(filename)) #Karate
    n = A.shape[1]
    k = np.array(A.sum(1)).reshape(n) # the degree sequence
    m = 0.5*A.sum() # the number of edges
    writename = os.path.basename(filename)
    filewriter = Matwriter(writename)
    t = time.time()
    louvain.louvain(A, m, n, k, filewriter)
    print "It took %s seconds" % (time.time() - t)

if __name__ == '__main__':
    main()