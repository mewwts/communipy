import os
import numpy as np

class Exporter(object):
    """
    Output community structure in .txt for use in different ways
    """
    def __init__(self, filename, n):
        writename = os.path.basename(filename)
        self.path = "".join(["results/", writename, "-communities.txt"])
        self.comlist = np.array(xrange(n))
        self.n = n

    def write_nodelist(self, com_dict):
        affiliation = np.repeat(-1, self.n)
        if len(self.comlist.shape) == 1:
            col = self.comlist
        else:
            col = self.comlist[:, -1]
        for key, val in com_dict.iteritems():
            print val
            affiliation[np.in1d(col, list(val))] = key
        if not np.all(col == affiliation):
            self.comlist = np.column_stack((self.comlist, affiliation))

    def make_list(self, com_dict):
        aff = np.zeros(self.n)
        for key, val in com_dict.iteritems():
            val = np.array(list(val))
            aff[val] = key
        return aff

    def close(self):
        np.savetxt(self.path, self.comlist, fmt='%i')
