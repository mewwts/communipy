import numpy as np
class Communities(object):

    def __init__(self, iterable, k):
        self._nodes = np.array(iterable)
        self._communities = {i:set([i]) for i in self._nodes}
        self._strength = {i:k[i] for i in xrange(len(k))}

    def move(self, i, s, k_i):
        s_i = self.get_community(i)
        self._communities[s_i].remove(i)
        if not self._communities[s_i]:
            del self._communities[s_i]
            del self._strength[s_i]
        try:
            self._strength[s_i] -= k_i    
        except KeyError:
            pass
        self._strength[s] += k_i
        self._nodes[i] = s
        self._communities[s].add(i)
        
    def get_community_strength(self, x):
        return self._strength[x]

    def get_community(self, x):
        return self._nodes[x]
 
    def get_neighbors(self, x):
        a = self._communities[self.get_community(x)]
        return np.array(a)

    def get_neighbors_not_i(self, x):
        a = self._communities[self.get_community(x)]
        return list(a.difference([x]))
        #return np.nonzero(self._nodes == self.get_community(x))[0]

    def get_nodes(self, s):
        try: 
            return list(self._communities[s])
        except KeyError:
            return []
        #return np.nonzero(self._nodes == s)[0]

    def get_node_list(self):
        return self._nodes

    def get_communities(self):
        return {key: list(value) for key, value in self._communities.iteritems()}#[list(a) for a in self._communities.values()]
        #return [ a for a in [np.nonzero(self._nodes == i)[0] for i in xrange(len(self._nodes))] if a.shape[0] > 0]
    
    def get_communities_renamed(self):
        # sort keys
        keys = sorted(self._communities.keys())
        # rename communities and return
        return {i:list(self._communities[x]) for i,x in enumerate(keys)}
