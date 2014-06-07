from communities import Communities

class Labels(Communities):

    def __init__(self, iterable, k, diagonal):
        super(Labels, self).__init__(iterable, k)
        self.internal = [diagonal[i] for i in iterable]
        # self.internal = [0.0] * len(self.nodes)
        self.d = [0.0] * len(self.nodes)
        self.p = [1.0/len(self.nodes)] * len(self.nodes)
