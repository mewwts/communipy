from math import ceil
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm, SymLogNorm
import seaborn as sns

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
    colormap = matplotlib.colors.LinearSegmentedColormap.from_list('colormap', sns.color_palette("YlOrRd_r", 8)[::-1])
    image=plt.imshow(bins, cmap=colormap, interpolation='none', vmin=0.0,norm = SymLogNorm(linthresh=0.001))
    
    ax.grid(False, which="major")
    ax.grid(False, which="minor")
    
    divider = make_axes_locatable(ax)
    color_ax = divider.append_axes("right", size="5%", pad=.5)
    plt.colorbar(image, cax=color_ax)
    
    # plt.savefig('results/sparsity.png', dpi=2000, bbox_inches='tight')  
    plt.show()