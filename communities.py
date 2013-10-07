import numpy as np
class Communities(object):

    def __init__(self, nodes):
        self._nodes = np.array(nodes)

    def move(self, x, s):
        self._nodes[x] = s
    
    def get_community(self, x):
        return self._nodes[x]

    def get_neighbors(self, x):
        return np.nonzero(self._nodes == self.get_community(x))[0]

    def get_nodes(self, s):
        return np.nonzero(self._nodes == s)[0]

    def get_communities(self):
        # implement with filter?
        return [ a for a in [np.nonzero(self._nodes == i)[0] for i in xrange(len(self._nodes))] if a.shape[0] > 0]
