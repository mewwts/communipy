import numpy as np
from scipy import io
import os

class Matwriter(object):

    def __init__(self, filename):
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
        self.name = "".join(["results/", writename, datestring])
    
    def write_nodelist(self, coms, n, iter):
        nodes = np.arange(n)
        comlist = np.zeros(n)
        for com in coms.iteritems():
            comlist[com[1]] = com[0]
        io.savemat(self.name, {"".join([self.name, '_nodes_', str(iter)]): nodes,
            "".join([self.name, '_communities_', str(iter)]): comlist}, oned_as='row', appendmat=True)
