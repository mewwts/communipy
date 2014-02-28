class Communities(object):

    def __init__(self, iterable, k):
        self._nodes = {}.fromkeys(iterable).keys()
        self._communities = {i:set([i]) for i in self._nodes}
        self._strength = {i:k[i] for i in xrange(len(k))}
        self._largest = (0, 1)

    def move(self, i, s, k_i):
        s_i = self.get_community(i)
        self._communities[s_i].remove(i)
        if not self._communities[s_i]:
            del self._communities[s_i]
            del self._strength[s_i]
        try: # Why not else here
            self._strength[s_i] -= k_i
        except KeyError:
            pass
        if s == -1:
            # Isolate vertex i
            for j in xrange(2*len(self._communities), 0, -1):
                if j not in self._communities:
                    self._communities[j] = {i}
                    self._strength[j] = k_i
                    self._nodes[i] = j
                    break
        else:
            self._strength[s] += k_i
            self._nodes[i] = s
            self._communities[s].add(i)
            size = len(self._communities[s])
            if size > self._largest[1]:
                self._largest = (s, size)

    def insert_community(self, nodes, k):
        newkey = -1
        for j in xrange(2*len(self._communities), 0, -1):
            if j not in self._communities:
                newkey = j
                self._communities[j] = {}
        for i, node in enumerate(nodes):
            self.move(node, newkey, k[i])

    def delete_community(self, c, k):
        nodes = self._communities[c].copy()
        for node in nodes:
            self.move(node, -1, k[node])

    def get_community_strength(self, x):
        return self._strength[x]

    def get_community(self, x):
        return self._nodes[x]

    def get_neighbors(self, x):
        return list(self._communities[self.get_community(x)])

    def get_neighbors_not_i(self, x):
        a = self._communities[self.get_community(x)]
        try:
            b = a.copy()
            b.remove(x)
            return list(b)
        except TypeError:
            return []

    def get_nodes(self, s):
        try:
            return list(self._communities[s])
        except KeyError:
            return []
        
    def get_node_list(self):
        return self._nodes

    def get_communities(self):
        return {key: list(value) for key, value in \
            self._communities.iteritems()}
        
    def get_communities_renamed(self):
        # sort keys
        keys = sorted(self._communities.keys())
        # rename communities and return
        return {i:list(self._communities[x]) for i, x in enumerate(keys)}

    def get_number_of_communities(self):
        return len(self._communities.keys())

    def get_largest_community(self):
        return self._largest

    def dump(self, i):
        import cPickle as pickle
        pickle.dump(self, open("".join(['pickled_', \
            'coms', str(i), '.p']), "wb"))
