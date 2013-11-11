import datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import operator as op
import os

import numpy as np

class Analyzer:
    def __init__(self, filename):
        plt.ioff()
        self.passes = []
        self.i = 0
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        #writename = os.path.basename(filename)
        writename = "lolse"
        self.name = "".join(["exports/", writename, 'CSD_plot', datestring])

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
        n = len(self.passes)
        max_val = 0
        min_val = 100000000000 
        for dictionary in self.passes:
            val = max(dictionary.iteritems(), key=op.itemgetter(1))[1]
            max_val = val if val > max_val else max_val
            val = min(dictionary.iteritems(), key=op.itemgetter(1))[1]
            min_val = val if val < min_val else min_val
        
        le_range = (min_val, max_val)
        fig = plt.figure(1)
        coms = [p.values() for p in self.passes]
        plt.hist(coms, range=le_range, align='mid', histtype='bar', alpha=0.5, label=['Pass ' + str(i+1) for i in range(n)])
        plt.legend()
        plt.title('Component Size Distribution')
        #plt.show()
        plt.savefig(self.name)