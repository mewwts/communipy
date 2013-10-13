import numpy as np
class Communities(object):

    def __init__(self, vector):
        self._nodes = np.array(vector)
        self._communities = {i:set([i]) for i in vector}
        #self._strength = {i:k_i for i,k_i in enumerate(k)}

    def move(self, x, s):
        s_x = self.get_community(x)
        self._communities[s_x].remove(x)
        if not self._communities[s_x]:
            del self._communities[s_x]
            #del self._strength[s_x]

        self._nodes[x] = s
        self._communities[s].add(x)

    
    def get_community(self, x):
        return self._nodes[x]

    def get_neighbors(self, x):
        a = self._communities[self.get_community(x)]
        return list(a)
        
        #return np.nonzero(self._nodes == self.get_community(x))[0]

    def get_nodes(self, s):
        try: 
            return list(self._communities[s])
        except KeyError:
            return []
        #return np.nonzero(self._nodes == s)[0]

    def get_communities(self):
        
        return [list(a) for a in self._communities.values()]
        #return [ a for a in [np.nonzero(self._nodes == i)[0] for i in xrange(len(self._nodes))] if a.shape[0] > 0]
