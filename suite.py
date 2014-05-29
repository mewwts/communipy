from __future__ import division
import argparse
import labelprop
import main
import numpy as np
import os
import glob
import tester
# from multiprocessing import Pool
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
    indices = results[:, -2].argmin(axis=0)
    try:
        idx = indices[0]
    except IndexError:
        idx = indices
    return idx

def test(root):
    with open('results/results.txt', 'a') as output:
        # output.write("File\tMI\tNMI\tVI\tNVI\n")
        output.write("\n")
        files = []
        ground_truth = glob.glob(root + '/*truth.dat')[0]
        walk = glob.glob(root + '/*walk.mat')[0]
        for filename in os.listdir(root):
            if filename not in set([os.path.basename(ground_truth), 
                                '.DS_Store', os.path.basename(walk)]):
                files.append("".join([root, filename]))

        map(lambda x: run_louvain(x, ground_truth, output), files)
        map(lambda x: diss_merge(x, ground_truth, output), files)
        map(lambda x: deg_rank(x, ground_truth, output), files)
        # map(lambda x: run_prop(x, ground_truth, output), files)


def run_louvain(f, truth, output):
    print(f)
    G = initialize_graph(f)
    
    results = [[],[],[],[]]
    known = tester.parse(truth)
    known -= 1
    numcoms = []
    for i in xrange(10):
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02, False, False, Method.luv)
        community_detect(G, arguments)

        hierarchy = arguments.exporter.comlist
        colresult = np.empty(shape=(hierarchy.shape[1], 4))
        lengths = []
        for j, column in enumerate(hierarchy.T):
            lengths.append(len(np.unique(column)))
            colresult[j, :] = tester.test(column, known)
        print colresult
        idx = get_best_column(colresult)
        found = colresult[idx, :]
        numcoms.append(lengths[idx])
        for j, elem in enumerate(found):
            results[j].append(elem)

    results = [sum(res)/len(res) for res in results]
    write(output, os.path.basename(f), results[0], results[1],
          results[2], results[3], sum(numcoms)/len(numcoms),
          len(np.unique(known)), "Luv")

def run_prop(f, truth, output):
    print(f)
    G = initialize_graph(f)
    
    results = [[],[],[],[]]
    known = tester.parse(truth)
    known -= 1
    for i in xrange(10):
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02, False, False, Method.prop)
        labelprop.propagate(G, arguments)
        found = arguments.exporter.comlist[:, -1]
        for j, elem in enumerate(tester.test(found, known)):
            results[j].append(elem)
    results = [sum(res)/len(res) for res in results]
    write(output, os.path.basename(f), results[0], results[1],
          results[2], results[3], len(np.unique(found)),
          len(np.unique(known)), "Prop")

def deg_rank(f, truth, output):
    print(f)
    G = initialize_graph(f)
  
    results = [[],[],[],[]]
    known = tester.parse(truth)
    known -= 1
    numcoms = []
    for i in xrange(10):
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02, False, False, Method.luv)
        community_detect(G, arguments)

        hierarchy = arguments.exporter.comlist
        colresult = np.empty(shape=(hierarchy.shape[1], 4))
        lengths = []
        for j, column in enumerate(hierarchy.T):
            lengths.append(len(np.unique(column)))
            colresult[j, :] = tester.test(column, known)
            
        idx = get_best_column(colresult)
        found = colresult[idx, :]
        numcoms.append(lengths[idx])
        for j, elem in enumerate(found):
            results[j].append(elem)

    results = [sum(res)/len(res) for res in results]
    write(output, os.path.basename(f), results[0], results[1],
          results[2], results[3], sum(numcoms)/len(numcoms),
          len(np.unique(known)), "Deg")

def diss_merge(f, truth, output):
    print(f)
    G = initialize_graph(f)

    results = [[],[],[],[]]
    known = tester.parse(truth)
    known -= 1
    numcoms = []
    for i in xrange(10):
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02, False, False, Method.luv)
        community_detect(G, arguments)

        hierarchy = arguments.exporter.comlist
        colresult = np.empty(shape=(hierarchy.shape[1], 4))
        lengths = []
        for j, column in enumerate(hierarchy.T):
            lengths.append(len(np.unique(column)))
            colresult[j, :] = tester.test(column, known)
            
        idx = get_best_column(colresult)
        found = colresult[idx, :]
        numcoms.append(lengths[idx])
        for j, elem in enumerate(found):
            results[j].append(elem)

    results = [sum(res)/len(res) for res in results]
    write(output, os.path.basename(f), results[0], results[1],
          results[2], results[3], sum(numcoms)/len(numcoms),
          len(np.unique(known)), "Dissolve")

def initialize_graph(f):
    A = main.get_graph(f)
    G = Graph(A,
              0.5*A.sum(),
              A.shape[1],
              np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist() 
              )
    return G

def write(output, f, mi, nmi, vi, nvi, n_found, n_known, method):
    output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
        f, mi, nmi, vi, nvi, n_found, n_known, method)
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_dir", 
                        help="Specify the path of the data set")
    args = parser.parse_args()
    if not os.path.isdir(args.path_to_dir):
        print("That's not a folder.")
    else:
        test(args.path_to_dir)
