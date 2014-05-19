import modularity
from labels import Labels
from heapdict import heapdict

class ModCommunities(Labels):

    def __init__(self, iterable, G):
        """
        Modularity holds {key: (0/1, priority)} pairs
        """
        super(ModCommunities, self).__init__(iterable, G.k)
        self.modularity = heapdict()
        self.node_mods = {}
        self.changed = False
        self.network_modularity = 0.0

        for i in iterable:
            q = modularity.single_node_modularity(G, i)
            self.modularity[i] = (0, q)
            self.node_mods[i] = q
            self.network_modularity += q

    def pop(self, i=0):
        """
        Pop the community with the lowest modularity, push it back
        (but with the first value of the tuple 1 and not 0) and return
        the item.

        Args:
        i: the index to pop. Default 0.

        Returns:
        (x, y, z): x the key of the community, y=0/y=1, z modularity of
        the community.

        """
        item_key, (item_seen, item_val) = self.modularity.peekitem()
        self.modularity[item_key] = (1, item_val)
        return item_key, (item_seen, item_val)

    def move(self, i, s, k_i, movein, moveout, quv):
        """
        Move a vertex from it's community to the community s.

        Args:
        i: the integer label of the vertex to be moved
        s: the destination of vertex i. May be -1 to indicate that we
           want to isolate the vertex.
        k_i: k[i], the degree of vertex i
        movein: The global modularity gain of moving vertex i to s.
        moveout: The global modularity loss of moving vertex i from it's
                 community.
        quv: q_s + movein + quv = q_s* the new modularity. If 
             mass_modularity is being used, remember to only add this 
             quantity once.

        """
        s_i = self.nodes[i]

        # remove i from it's community
        self.communities[s_i].remove(i)

        # if there's no nodes left, remove community from dicts
        if not self.communities[s_i]:
            del self.communities[s_i]
            del self.strength[s_i]
            self.network_modularity -= self.modularity[s_i][1]
            del self.modularity[s_i]
        
        # key might not be in strength, since we might have deleted it
        try:
            self.strength[s_i] -= k_i
        except KeyError:
            #The community has been deleted.
            pass

        # same goes for modularity
        try:
            (seen, mod) = self.modularity[s_i]
        except KeyError:
            #The community has been deleted.
            pass 
        else:
            self.modularity[s_i] = (seen, mod - moveout + quv)
            self.network_modularity -= moveout
            self.network_modularity += quv

        if s == -1:
            # Isolate vertex i
            j = self._unused_key()
            self.communities[j] = set([i])
            self.strength[j] = k_i
            self.nodes[i] = j
            self.modularity[j] = (0, quv)
            self.network_modularity += quv

        else:
            self.nodes[i] = s
            self.communities[s].add(i)
            self.strength[s] += k_i
            (seen, mod) = self.modularity[s]
            self.modularity[s] = (seen, mod + movein + quv)
            self.network_modularity += (movein + quv) 

    def unsee_all(self):
        for key, (seen, val) in self.modularity.iteritems():
            self.modularity[key] = (0, val)
