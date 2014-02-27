from communities import Communities

class Labels(Communities):

    def __init__(self, iterable, k):
        super(Labels, self).__init__(iterable, k)
        self._internal = k[:]
        self._d = [0.0] * len(self._nodes)
        self._p = [1.0/len(self._nodes)] * len(self._nodes)

    def move(self, i, s, k_i, intra=None):
        super(Labels, self).move(i, s, k_i)
        if intra is not None:
            try:
                self._internal[i] = intra
            except IndexError:
                'Warning, IndexError: No such vertex in list.'

    def get_internal(self, i):
        try:
            a = self._internal[i]
        except IndexError:
            'Warning, IndexError: No such vertex in list.'
        else:
            return a

    def set_d(self, i, di):
        try:
            self._d[i] = di
        except IndexError:
            print 'Warning, IndexError: No such vertex in list.'
    
    def get_d(self, i):
        try:
            d = self._d[i]
        except IndexError:
            print 'Warning, IndexError: No such vertex in list.'
        else:
            return d

    def set_p(self, i, pi):
        try:
            self._p[i] = pi
        except IndexError:
            print 'Warning, IndexError: No such vertex in list.'
    
    def get_p(self, i):
        try:
            p = self._p[i]
        except IndexError:
            print 'Warning, IndexError: No such vertex in list.'
        else:
            return p
