import csv
import numpy as np
import os

class Cytowriter:

    def __init__(self, filename, tsh):
        self._i = 1
        self._tsh = tsh
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
        self._name = "".join(["exports/", writename, '_to_cyto_', datestring])
        self._array = None
        self._nodes = np.array([], dtype=int)

    def add_pass(self, comdict, A = None):
        if self._i == 1:
            comdict = {key:nodes for key, nodes in comdict.iteritems() if len(nodes) >= self._tsh}
            for k,v in comdict.iteritems():
                self._nodes = np.hstack((self._nodes, np.array(v)))
            ivals = np.array([k for k in comdict.keys() for j in comdict[k]], dtype=int)
            jvals = np.array([v for r in comdict.keys() for v in comdict[r]], dtype=int)
            n = len(ivals)
            # self._array = np.empty((n, 2), dtype = int)
            self._array = np.column_stack((jvals, ivals))
            if A != None:
                self._export_sif(A)

        else:
            n = self._array.shape[0]
            self._array = np.column_stack((self._array, np.empty((n, 1), dtype=int)))
            for key, val in comdict.iteritems():
                rows = np.in1d(self._array[:,self._i-1], val)
                m = len(np.nonzero(rows))
                self._array[rows, self._i] = np.repeat(np.array([key]), m)
            if np.all(self._array[:,self._i - 1 ] == self._array[:, self._i]):
                self._array = self._array[:, :-1]
        self._i += 1

    def close(self):
        np.savetxt("".join([self._name, '.csv']), self._array, delimiter=";", fmt='%i')

    def _export_sif(self, A):
        A = A[self._nodes,:][:, self._nodes]
        n = A.shape[1]
        with open("".join([self._name, 'adjlist' ,'.sif']), 'w') as new:
            for i in xrange(n):
                data = A.data[A.indptr[i]:A.indptr[i+1]]
                indices = A.indices[A.indptr[i]:A.indptr[i+1]]
                s = " ".join(map(str, indices[indices>=i]))
                new.write('%d 1 %s \n' % (i, s))