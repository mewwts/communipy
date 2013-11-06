import datetime as dt
import matplotlib.pyplot as plt

import os

import numpy as np

class Analyzer:
    def __init__(self, filename):
        self.passes = []
        self.i = 0
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
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
        fig = plt.figure(1)
        for i, passi in enumerate(self.passes):
            com = passi.values()
            fig.add_subplot(2,2,i)
            plt.title('Iteration ' + str(i + 1))
            plt.hist(com, bins=max(com),align='mid', histtype='bar', facecolor='g', alpha=0.75)
        plt.suptitle('Component Size Distribution')
        plt.savefig(self.name)