from __future__ import division
import argparse
import labelprop
import main
import numpy as np
import os
import tester
from multiprocessing import Pool
from export_communities import Exporter
from utils import Graph, Arguments, Method
from community_detection import community_detect

def get_right_column(comlist, ncom):
    smallest = (-1, 99999999999)
    for i in xrange(comlist.shape[1]):
        uniq = len(np.unique(comlist[:,i]))
        if abs(uniq - ncom) < smallest[1]:
            smallest = (i, uniq - ncom)
    return comlist[:, smallest[0]]

def get_best_column(results):
    """ Get the result that minimizes the NVI. """
    indices = results[:, -2].argmin(axis=0)
    try:
        idx = indices[0]
    except IndexError:
        idx = indices
    return idx

def get_files(dir):
    file_list = []
    for root, dirs, files in os.walk(dir):
        dir_files = []
        for f in files:
            if f.endswith('truth.dat'):
                truth = "/".join([root, f])
            elif (not f.endswith('walk.dat') and
                  not f.endswith('.DS_Store')):
                dir_files.append("/".join([root, f]))
        if files:
            file_list.append((dir_files, truth))
    return file_list


def format(f, mi, nmi, vi, nvi, n_found, n_known, method):
    return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  f, mi, nmi, vi, nvi, n_found, n_known, method)


class Run(object):

    def __init__(self, truth, method):
        self.truth = truth
        self.method = method

    def __call__(self, f):
        print(self.method)
        print(f)
        G = initialize_graph(f)
        results = [[],[],[],[]]
        known = tester.parse(self.truth)
        known -= 1
        numcoms = []
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02,
                              False, False, self.method)
        if self.method == Method.prop:
            labelprop.propagate(G, arguments)
            found = arguments.exporter.comlist[:, -1]
            numcoms = np.unique(found)
            results = tester.test(found, known)
        else:
            community_detect(G, arguments)
            hierarchy = arguments.exporter.comlist
            colresult = np.empty(shape=(hierarchy.shape[1], 4))
            lengths = []

            for j, column in enumerate(hierarchy.T):
                lengths.append(len(np.unique(column)))
                colresult[j, :] = tester.test(column, known)

            idx = get_best_column(colresult)
            results = colresult[idx, :]
            numcoms = lengths[idx]
                
        return format(os.path.basename(f), results[0], results[1],
                results[2], results[3], numcoms,
                len(np.unique(known)), str(arguments.method).split('.')[-1])

def initialize_graph(f):
    A = main.get_graph(f)
    G = Graph(A,
              0.5*A.sum(),
              A.shape[1],
              np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist()
              )
    return G

def output_to_file(filename, results):

    with open(filename, 'a+') as output:
        if not output.readline():
            output.write("File\tMI\tNMI\tVI\tNVI\tn_found\tn_known\tmethod\n")
        for line in results:
            output.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_dir", 
                        help="Specify the path of the data set")
    parser.add_argument("n", 
                        help="The number of runs for each data set")
    args = parser.parse_args()
    results = []
    def res_app(res):
        results.append(res)
    if not os.path.isdir(args.path_to_dir):
        print("That's not a folder.")
    else:
        pool = Pool()
        files = get_files(args.path_to_dir)


        for fs, ground_truth in files:
            for f in fs:
                for i in xrange(int(args.n)):
                    pool.apply_async(Run(ground_truth, Method.luv), 
                        args=(f, ),
                        callback=res_app)
                    pool.apply_async(Run(ground_truth, Method.dissolve), 
                        args=(f, ), 
                        callback=res_app)
                    pool.apply_async(Run(ground_truth, Method.rank), 
                        args=(f, ),
                        callback=res_app)
                    pool.apply_async(Run(ground_truth, Method.prop), 
                        args=(f, ),
                        callback=res_app)
        pool.close()
        pool.join()
        output_to_file('results/results.txt', results)
        print("Tests ended just fine.")