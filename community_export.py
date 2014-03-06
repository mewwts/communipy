import numpy as np
import os

class Exporter(object):
    """
    Output community structure for use in different ways
    """
    def __init__(self, filename):
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
        self.path = "".join(["results/", writename, datestring, '.gz'])
        self.comlist = None

    def write_nodelist(self, coms):
        if self.comlist == None:
            self.comlist = coms
        else:
            np.column_stack((self.comlist, coms))

    def close(self):
        np.savetxt(self.path, self.comlist)
