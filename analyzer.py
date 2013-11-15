import datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import operator as op
import os
from math import ceil, log, floor
import numpy as np

class Analyzer:
    def __init__(self, filename):
        plt.ioff()
        self.passes = []
        self.i = 0
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
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
        n = len(self.passes)
        max_val = 0
        min_val = 100000000000 
        for dictionary in self.passes:
            val = max(dictionary.iteritems(), key=op.itemgetter(1))[1]
            max_val = val if val > max_val else max_val
            val = min(dictionary.iteritems(), key=op.itemgetter(1))[1]
            min_val = val if val < min_val else min_val
        
        order = 10**floor(log(max_val, 10))

        le_range = (0, ceil(float(max_val)/order)*order)
        colors = ['b', 'g', 'r', 'm']
        plt.figure(figsize=(15,15), dpi=100)
        plt.title('Component Size Distribution')
        # coms = [p.values() for p in self.passes]
        n = float(len(self.passes))

        for i,p in enumerate(self.passes):

            plt.subplot(2,ceil(n/2),i+1)
            plt.xlabel('Size')
            plt.ylabel('# communities')
            com = p.values()
            #hist = np.bincount(com)
            #x = np.arange(0,len(hist),step=1)
            plt.title('Pass ' + str(i + 1))
            #plt.bar(x, hist, color = colors[i % 4], width=1, align='center')
            plt.ylim(0,5)
            plt.xlim(0,max_val+0.5)
            #le_bins = np.append(np.arange(0, le_range[1], le_range[1]/10), le_range[1])
            ns, bins, patches = plt.hist(com, range=le_range, bins=le_range[1]/order, align='mid', histtype='bar', alpha=0.5, label=['Pass ' + str(i)])
            plt.xlim((0,le_range[1]))
            
        plt.savefig(self.name)