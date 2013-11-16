import datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import operator as op
import os
from math import ceil, log, floor
import numpy as np
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
        n = len(self.passes)
        max_val = 0
        min_val = 100000000000 
        for dictionary in self.passes:
            val = max(dictionary.iteritems(), key=op.itemgetter(1))[1]
            max_val = val if val > max_val else max_val
        
        order = 10**floor(log(max_val, 10))

        le_range = (0, ceil(float(max_val)/order)*order)
        colors = ['indianred', 'tan', 'cadetblue', 'seagreen']
        plt.figure(dpi=100)
        plt.title('Component Size Distribution')
        # coms = [p.values() for p in self.passes]
        bin_num = le_range[1]/order
        while bin_num < 4:
            bin_num *=2
        max_height = 0
        
        for i,p in enumerate(self.passes):

            plt.subplot(ceil(n/2.0),2, i+1)
            plt.xlabel('Size')
            plt.ylabel('# communities')
            com = p.values()
            plt.title('Pass ' + str(i+1))
            #plt.ylim(0, 5)
            plt.xlim(0, max_val)
            ns, bins, patches = plt.hist(com, range=le_range, bins=bin_num, align='mid', histtype='bar', alpha=0.5, label=['Pass ' + str(i)], color=colors[i % len(colors)])
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
            plt.xlim((0, le_range[1]))
            m = max(p.get_height() for p in patches)
            max_height = m if m > max_height else max_height
        plt.ylim(0, max_height)
        plt.show()    
        plt.savefig(self.name)
