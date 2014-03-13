from communities import Communities

class Labels(Communities):

    def __init__(self, iterable, k):
        super(Labels, self).__init__(iterable, k)
        self.internal = [sum(k[i] for i in self[j]) for j in self.dict.keys()]
        self.d = [0.0] * len(self.nodes)
        self.p = [1.0/len(self.nodes)] * len(self.nodes)

    def move(self, i, s, k_i, intra=None):
        super(Labels, self).move(i, s, k_i)
        if intra is not None:
            try:
                self.internal[i] = intra
            except IndexError:
                'Warning, IndexError: No such vertex in list.'

    def recluster(self, com_dict, k):
        super(Labels, self).recluster(com_dict, k)
        # Should avoid this iteration
        for name, coms in com_dict.iteritems():
            for c_i in coms[1:]:
                for i in self[c_i]:
                    # WILD approximation
                    self._internal[i] = k - self._internal[i]
