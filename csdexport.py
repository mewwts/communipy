import datetime as dt
import operator as op
import os
from math import ceil, log, floor
import numpy as np
import cPickle as pickle


class Csdwriter:
    def __init__(self, filename):
        self.passes = []
        self.i = 0
        writename = os.path.basename(filename)
        self.name = "".join(["exports/", writename])

    def add_pass(self, coms):
        if self.i == 0:
            self.passes.append({key:len(val) for key, val in coms.iteritems()})
        else:
            self.passes.append({key:0 for key, val in coms.iteritems()})
            for key,val in coms.iteritems():
                for v in val:
                    self.passes[self.i][key] += self.passes[self.i-1][v]
        self.i +=1

    def show(self):
        pickle.dump(self.passes, open("".join(['MAT_MIN_LCC_coms','.p']), "wb" ))
