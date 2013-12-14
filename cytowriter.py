import csv
import numpy as np
import os

class Visualizer:

    def __init__(self, filename, tsh, passnr, compass):
        self._pass = passnr -1 
        self._compass = compass -1
        self._i = 1
        self._tsh = tsh
        writename = os.path.basename(filename)
        self._name = "".join(["exports/", writename])
        self._array = None
        self._nodes = np.array([], dtype=int)
        self._communities = {}

    def add_pass(self, comdict, A = None):
        print self._i
        if self._i == self._pass:
            self._export_edgelist(A)

        if self._i == self._compass:
            self.close()
        if self._i == 1:
            for key, value in comdict.iteritems():
                if len(value) > 0:
                    self._communities[key] = set(value)
        else:
            new_dict = {}
            for key, value in comdict.iteritems():    
                new_dict[key] = set.union(*[self._communities[v] for v in value])
            self._communities = new_dict
        

        self._i += 1       

        # if self._i == 1:
        #     comdict = {key:nodes for key, nodes in comdict.iteritems() if len(nodes) >= self._tsh}
        #     for k,v in comdict.iteritems():
        #         self._nodes = np.hstack((self._nodes, np.array(v)))
        #     ivals = np.array([k for k in comdict.keys() for j in comdict[k]], dtype=int)
        #     jvals = np.array([v for r in comdict.keys() for v in comdict[r]], dtype=int)
        #     n = len(ivals)
        #     self._array = np.column_stack((jvals, ivals))
        # else:
        #     n = self._array.shape[0]
        #     self._array = np.column_stack((self._array, np.empty((n, 1), dtype=int)))
        #     for key, val in comdict.iteritems():
        #         rows = np.in1d(self._array[:,self._i-1], val)
        #         m = len(np.nonzero(rows))
        #         self._array[rows, self._i] = np.repeat(np.array([key]), m)
        #     if np.all(self._array[:,self._i - 1 ] == self._array[:, self._i]):
        #         self._array = self._array[:, :-1]
        

    def close(self):
        # a = self._array[:, (0, self._compass-1)].copy()
        # a = np.unique(a.view(np.dtype((np.void, a.dtype.itemsize*a.shape[1])))).view(a.dtype).reshape(-1, a.shape[1])
        ivals = np.fromiter((k for k in self._communities.keys()), dtype=int)
        jvals = np.fromiter((len(self._communities[r]) for r in self._communities.keys()),dtype=int)
        a = np.column_stack((ivals, jvals))
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
