import csv
import numpy as np
import os

class Visualizer:

    def __init__(self, filename, tsh, passnr, compass):
        self._pass = passnr
        self._compass = compass
        self._i = 1
        self._tsh = tsh
        import datetime as dt
        writename = os.path.basename(filename)
        self._name = "".join(["exports/", writename])
        self._array = None
        self._nodes = np.array([], dtype=int)

    def add_pass(self, comdict, A = None):
        if self._i == self._pass:
            self._export_edgelist(A)

        if self._i == 1:
            comdict = {key:nodes for key, nodes in comdict.iteritems() if len(nodes) >= self._tsh}
            for k,v in comdict.iteritems():
                self._nodes = np.hstack((self._nodes, np.array(v)))
            ivals = np.array([k for k in comdict.keys() for j in comdict[k]], dtype=int)
            jvals = np.array([v for r in comdict.keys() for v in comdict[r]], dtype=int)
            n = len(ivals)
            self._array = np.column_stack((jvals, ivals))
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
        a = self._array[:, (0, self._compass-1)].copy()
        a = np.unique(a.view(np.dtype((np.void, a.dtype.itemsize*a.shape[1])))).view(a.dtype).reshape(-1, a.shape[1])
        np.savetxt("".join([self._name, 'coms' '.txt']), a, delimiter=";", fmt='%i')

    def _export_edgelist(self, A):
        n = A.shape[1]
        with open("".join([self._name, 'adjlist' ,'.txt']), 'w') as new:
            for i in xrange(n):
                data = A.data[A.indptr[i]:A.indptr[i+1]]
                indices = A.indices[A.indptr[i]:A.indptr[i+1]]
                # s = " ".join(map(str, indices[indices>=i]))
                for ind, j in enumerate(indices):
                    new.write('%d %d %d \n' % (i, j, data[ind]))
