# Extract data to preprocessed-data
import numpy as np
from os import mkdir
from glob import glob
import mahotas as mh
from itertools import chain


_min_obj_size = 32
def as_labeled(fname):
    '''Load the image as a labeled image'''
    # Read the image
    im  = mh.imread(fname)
    # borders are saved as red lines
    borders = (im[:,:,0] > im[:,:,1])

    # first labeling
    labeled,N = mh.label(~borders)
    
    
    # with modern mahotas, this would be done with mh.labeled.labeled_size()
    # but this function did not exist when the paper was written
    bg = 0
    bg_size = (labeled==bg).sum()
    for i in range(1, N+1):
        i_size = (labeled == i).sum()
        if i_size > bg_size:
            bg_size = i_size
            bg = i
        if i_size < _min_obj_size:
            labeled[labeled==i] = 0
    labeled[labeled==bg]=0
    labeled,_ = mh.label(labeled!=0)
    assert labeled.max() < 256
    return labeled.astype(np.uint8)

ic100 = glob('data/images/segmented-lpc/ic100/dna-*.xcf')
gnf = glob('data/images/segmented-lpc/gnf/dna-*.xcf')

mkdir('preprocessed-data/')
mkdir('preprocessed-data/ic100')
mkdir('preprocessed-data/gnf')
for fpath in chain(ic100, gnf):
    ofile = fpath.replace('data/images/segmented-lpc/', 'preprocessed-data/') \
            .replace('.xcf','.png')
    mh.imsave(ofile, as_labeled(fpath))

print('Data is now available inside the directory preprocessed-data/ in PNG format')
