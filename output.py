from scipy import io
import os

class Matwriter(object):

    def __init__(self, filename):
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        writename = os.path.basename(filename)
        self.name = "".join(["results/", writename, datestring])
    
    def write_array(self, key, list):
        io.savemat(self.name, {key: list}, oned_as='row', appendmat=True)
        print key, list
    
