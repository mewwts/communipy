import numpy as np
from scipy import io
import os

class Matwriter(object):

    def __init__(self, filename):
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
        self.name = "".join(["results/", writename, datestring])
        self.dict = {}

    def write_nodelist(self, coms, n, iter):
        nodes = np.arange(n, dtype=int)
        comlist = np.zeros(n, dtype=int)
        for com in coms.iteritems():
            comlist[com[1]] = com[0]
        self.dict["".join(['nodes_', str(iter)])] = nodes
        self.dict["".join(['communities_', str(iter)])] = comlist
    
    def close(self):
        io.savemat(self.name, self.dict, oned_as='row', appendmat=True) 
