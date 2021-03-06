
class Communities(object):
    """
    This class represents a community structure. A collection of 
    disjoint sets(communities) such that all vertices in a graph are found in
    exactly one such set.

    """
    def __init__(self, iterable, k):
        """
        Initialize the community-object by a iterable specifying a 
        vertex -> community mapping. 

        Args:
        iterable: Iterable such that the i'th element specifies 
                  the community affiliation of vertex i.
        k: Degree sequence of same length as 'iterable'.

        """
        self.nodes = list(iterable)
        self.communities = {}
        self.strength = {}
        self.used = set([])
        for i, c in enumerate(iterable):
            if c not in self.communities:
                self.communities[c] = set([i])
                self.strength[c] = k[i]
                self.used.add(c)
            else:
                self.communities[c].add(i)
                self.strength[c] += k[i]

        
    def move(self, i, s, k_i):
        """
        Move the vertex i to community s.

        Args:
        i: the integer label of the vertex that is moving
        s: the destination(new community) of i
        k_i: the degree of i

        """

        s_i = self.nodes[i]

        # remove i from it's community
        self.communities[s_i].remove(i)

        # if there's no nodes left, remove community from dicts
        if not self.communities[s_i]:
            del self.communities[s_i]
            del self.strength[s_i]
        # key might not be in strength
        try:
            self.strength[s_i] -= k_i
        except KeyError:
            pass

        if s == -1:
            # Isolate vertex i
            j = self._unused_key()
            self.communities[j] = set([i])
            self.strength[j] = k_i
            self.nodes[i] = j
        else:
            self.nodes[i] = s
            self.strength[s] += k_i
            self.communities[s].add(i)

    def insert_community(self, nodes, k):
        newkey = self._unused_key()
        self.communities[newkey] = set([])
        self.strength[newkey] = 0
        for node in nodes:
            self.move(node, newkey, k[node])

    def delete_community(self, c, k):
        nodes = self.communities[c].copy()
        for node in nodes:
            self.move(node, -1, k[node])
 
    def _unused_key(self):
        for j in xrange(4*len(self.nodes), 0, -1):
            if j not in self.used:
                self.used.add(j)
                return j
        raise Exception("Couldn't find key")

    def neighbors(self, x):
        a = self.communities[self.get_community(x)]
        try:
            b = a.copy()
            b.remove(x)
            return list(b)
        except TypeError:
            return []
    
    def size(self, c):
        return len(self.communities[c])

    @property
    def dict(self):
        return {key: list(value) for key, value in 
                self.communities.iteritems()}

    @property
    def dict_renamed(self):
        # sort keys
        keys = sorted(self.communities.keys())
        # rename communities and return
        return {i:list(self.communities[x]) for i, x in enumerate(keys)}

    def dump(self, i):
        import cPickle as pickle
        pickle.dump(self, open("".join(['pickled_', \
            'coms', str(i), '.p']), "wb"))

    def recluster(self, com_dict, k):
        for name, coms in com_dict.iteritems():
            for c_i in coms[1:]:
                 for i in self.getnodes(c_i):
                    self.move(i, coms[0], k[i])
    @property
    def largest(self):
        largest = (-1, -1)
        for c, nodes in self.communities.iteritems():
            if len(nodes) > largest[1]:
                largest = (c, len(nodes))
        return largest[0]

    def __iter__(self):
        for key in self.communities.keys():
            yield (key, list(self.communities[key]))

    def __getitem__(self, c_i):
        try:
            com = self.communities[c_i]
        except KeyError:
            com = set([])
        return com

    def __len__(self):
        return len(self.communities)
