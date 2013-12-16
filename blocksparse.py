from math import ceil
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns


# based on : http://redmine.epfl.ch/projects/python_cookbook/wiki/Matrix_sparsity_patterns#Source-code-binningpy

def blocks(A, nblocks):
    n = A.shape[0]
    block_size = ceil(float(n)/float(nblocks))
    blocks = np.zeros((nblocks, nblocks))
    for i in xrange(nblocks):
        starti = i*block_size
        stopi = (i+1)*block_size
        if stopi > n:
                stopi = n

        for j in xrange(nblocks):
            startj =j*block_size
            stopj = (j+1)*block_size
            if stopj > n:
                stopj = n
            blocks[i,j] = A[starti:stopi, :][:, startj:stopj].sum()
    
    return blocks, block_size

def plot_block_sparsity_structure(A, nblocks):
    bins, ss = blocks(A, nblocks)
    
    plt.figure()
    
    ax=plt.subplot(111)
    my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('my_cmap', sns.color_palette("YlOrRd_r", 8)[::-1])
    im=plt.imshow(bins, cmap=my_cmap, interpolation='none', vmin=0.0)
    ax.grid(False, which="major")
    ax.grid(False, which="minor")
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=.5)
    plt.colorbar(im, cax=cax)
    
    plt.savefig('results/sparsity.png', dpi=2000, bbox_inches='tight')  