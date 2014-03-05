class Communities(object):

    def __init__(self, iterable, k):
        self.nodes = {}.fromkeys(iterable).keys()
        self.communities = {i:set([i]) for i in self.nodes}
        self.strength = {i:k[i] for i in xrange(len(k))}
        self._largest = (0, 1)

    def move(self, i, s, k_i):
        s_i = self.affiliation(i)
        self.communities[s_i].remove(i)

        if not self.communities[s_i]:
            del self.communities[s_i]
            del self.strength[s_i]

        try: # Why not else here
            self.strength[s_i] -= k_i
        except KeyError:
            pass

        if s == -1:
            # Isolate vertex i
            for j in xrange(2*len(self.communities), 0, -1):
                if j not in self.communities:
                    self.communities[j] = {i}
                    self.strength[j] = k_i
                    self.nodes[i] = j
                    break
        else:
            self.strength[s] += k_i
            self.nodes[i] = s
            self.communities[s].add(i)
            size = len(self.communities[s])
            if size > self._largest[1]:
                self._largest = (s, size)

    def insert_community(self, nodes, k):
        newkey = -1
        for j in xrange(2*len(self.communities), 0, -1):
            if j not in self.communities:
                newkey = j
                self.communities[j] = {}
        for i, node in enumerate(nodes):
            self.move(node, newkey, k[i])

    def delete_community(self, c, k):
        nodes = self.communities[c].copy()
        for node in nodes:
            self.move(node, -1, k[node])
 
    def affiliation(self, x):
        return self.nodes[x]

    def neighbors(self, x):
        a = self.communities[self.get_community(x)]
        try:
            b = a.copy()
            b.remove(x)
            return list(b)
        except TypeError:
            return []

    def get_node_list(self):
        return self.nodes

    @property
    def dict(self):
        return {key: list(value) for key, value in \
            self.communities.iteritems()}

    @property
    def dict_renamed(self):
        # sort keys
        keys = sorted(self.communities.keys())
        # rename communities and return
        return {i:list(self.communities[x]) for i, x in enumerate(keys)}

    @property
    def length(self):
        return len(self.communities.keys())

    @property
    def largest(self):
        return self._largest

    def dump(self, i):
        import cPickle as pickle
        pickle.dump(self, open("".join(['pickled_', \
            'coms', str(i), '.p']), "wb"))

    def recluster(self, com_dict, k):
        for name, coms in com_dict.iteritems():
            for c_i in coms[1:]:
                 for i in self.getnodes(c_i):
                    self.move(i, coms[0], k[i])

    def __iter__(self):
        for name, nodes in self.communities.iteritems():
            yield (name, list(nodes))

    def __getitem__(self, c_i):
        try:
            com = self.communities[c_i]
        except KeyError:
            com = []
        return list(com)
