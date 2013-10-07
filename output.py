from scipy import io

class Matwriter(object):

    def __init__(self, datastring):
        import datetime as dt
        datestring = dt.datetime.now().strftime("%Y-%m-%d-%M-%S")
        self.name = "".join(["results/", datastring, datestring])
    
    def write_array(self, key, list):
        io.savemat(self.name, {key: list}, oned_as='row')
        #print key, list
