import numpy as np
from scipy import io, sparse

def power(A, exp, path):
    indptr = A.indptr
    indices = A.indices
    nz = A.nonzero()
    
    # A is now A^exp
    for i in xrange(int(exp)-1):
        A = A.dot(A)

    data = np.empty(len(indices))
    for i, (x,y) in enumerate(zip(nz[0], nz[1])):
        data[i] = A[x,y]

    Ak = sparse.csr_matrix((data, indices, indptr))

    io.savemat(path, {'mat': Ak}, do_compression=True, oned_as='row')
