import datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import operator as op
import os
from math import ceil, log, floor
import numpy as np
import cPickle as pickle
try:
    import seaborn as sns
    sns.set_color_palette("deep", desat=.6)
except ImportError:
    print 'Fancy plots disabled as Seaborn is not installed'

class Analyzer:
    def __init__(self, filename):
        plt.ioff()
        self.passes = []
        self.i = 0
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        writename = os.path.basename(filename)
        #writename = "lolse"
        self.name = "".join(["exports/", writename, '_CSD_plot_', datestring])

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
