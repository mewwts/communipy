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
    """ 
    Return the column of comlist that has closest to ncom unique entries

    """
    smallest = (-1, 99999999999)
    for i in xrange(comlist.shape[1]):
        uniq = len(np.unique(comlist[:,i]))
        if abs(uniq - ncom) < smallest[1]:
            smallest = (i, uniq - ncom)
    return comlist[:, smallest[0]]

def get_best_column(result_matrix):
    """ Get the index of the column that minimizes the NVI. """
    indices = result_matrix[:, -2].argmin(axis=0)
    try:
        idx = indices[0]
    except IndexError:
        idx = indices
    return idx

def get_files(dir):
    """
    Recursively walks through all folder within 'dir' and outputs 
    the paths of all the files together with the file specifying
    the ground truth community structure.

    """
    file_list = []
    for root, dirs, files in os.walk(dir):
        dir_files = []
        for f in files:
            if f.endswith('truth.dat'):
                truth = os.path.join(root, f)
            elif (not f.endswith('walk.mat') and
                  not f.endswith('.DS_Store')):
                dir_files.append(os.path.join(root, f))
        if files:
            file_list.append((dir_files, truth))
    return file_list


def format(f, mi, nmi, vi, nvi, n_found, n_known, method):
    """ Return the arguments as a tab-delimitered string """
    return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  f, mi, nmi, vi, nvi, n_found, n_known, method)

class Run(object):
    """
    This class is used to run one of the community detection methods,
    gather the community structure, and test it against the ground
    truth.

    """
    def __init__(self, truth, method):
        """
        Instantiate the object with a ground truth and a method.

        Args:
        truth: the ground truth community structure of the network
               it will be run on.
        method: A constant indicating what method the object will run
                when called.

        """
        self.truth = truth
        self.method = method

    def __call__(self, f):
        """
        When the object is called like a function, we run the method
        specified by self.method on the dataset in file 'f'.
        
        Args:
        f: path to file where the network corresponding the the ground 
           truth community structure lies.

        Returns:
        A string of test results.

        """
        print(self.method)
        print(f)
        G = initialize_graph(f)
        known = tester.parse(self.truth)
        known -= 1
        exporter = Exporter(f, G.n, False)
        arguments = Arguments(exporter, None, None, 0.02,
                              False, False, self.method)
        if self.method == Method.prop:
            labelprop.propagate(G, arguments)
            found = arguments.exporter.comlist[:, -1]
            numcoms = len(np.unique(found))
            test_results = tester.test(found, known)
        else:
            community_detect(G, arguments)
            hierarchy = arguments.exporter.comlist[:, 1:] # Exclude the 0...n col
            colresult = np.empty(shape=(hierarchy.shape[1], 4))
            lengths = []

            for j, column in enumerate(hierarchy.T):
                lengths.append(len(np.unique(column)))
                colresult[j, :] = tester.test(column, known)

            idx = get_best_column(colresult)
            test_results = colresult[idx, :]
            numcoms = lengths[idx]
                
        return format(os.path.basename(f), test_results[0], test_results[1],
                test_results[2], test_results[3], numcoms,
                len(np.unique(known)), str(arguments.method).split('.')[-1])

def initialize_graph(f):
    """ Helper method to load file and make the Graph named tuple """
    A = main.get_graph(f)
    G = Graph(A,
              0.5*A.sum(),
              A.shape[1],
              np.array(A.sum(axis=1), dtype=float).reshape(-1,).tolist()
              )
    return G

def output_to_file(filename, results):
    """
    Write the array of result-strings 'results' to the file 'filename'.
    Will write a header if one is missing.
    """
    with open(filename, 'a+') as output:
        output.seek(0)
        if not output.readline():
            output.write("File\tMI\tNMI\tVI\tNVI\tn_found\tn_known\tmethod\n")
        else:
            output.seek(0, 2) # Put cursor at the end of the file.
        for line in results:
            output.write(line)

if __name__ == '__main__':
    """ Run the tests using the multiprocessing module """
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_dir", 
                        help="Specify the path of the data set")
    parser.add_argument("n", 
                        help="The number of runs for each data set")
    args = parser.parse_args()

    result_strings = []
    def res_app(res):
        result_strings.append(res)

    if not os.path.isdir(args.path_to_dir):
        print("That's not a folder.")
    else:
        pool = Pool()
        files = get_files(args.path_to_dir)
        for fs, ground_truth in files:
            for f in fs:
                # rank is deterministic
                pool.apply_async(Run(ground_truth, Method.rank), 
                    args=(f, ),
                    callback=res_app)
                for i in xrange(int(args.n)):
                    #Louvain, dissolve and labelprop are not, so we average
                    pool.apply_async(Run(ground_truth, Method.luv), 
                        args=(f, ),
                        callback=res_app)
                    pool.apply_async(Run(ground_truth, Method.dissolve), 
                        args=(f, ), 
                        callback=res_app)
                    pool.apply_async(Run(ground_truth, Method.prop), 
                        args=(f, ),
                        callback=res_app)
        pool.close()
        pool.join()
        output_to_file('results/results.txt', result_strings)
        print("Tests ended just fine.")