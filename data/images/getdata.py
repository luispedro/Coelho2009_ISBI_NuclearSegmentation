from __future__ import with_statement, division
import sys
import pyslic
import random
import os
import os.path
import numpy
from scipy.misc.pilutil import imsave

def maybe_mkdir(dir):
    '''
    mkdir(dir) if not exists(dir)
    '''
    if not os.path.exists(dir):
        os.mkdir(dir)

def as_colourimg(dna):
    '''
    This makes it a bit easier to work with the resulting images.
    '''
    return numpy.dstack((dna,dna,dna))

def get_gnf():
    imgs=pyslic.image.io.readtjz_recursive('raw-data/2007-07-24_Liso_vs._Mito/G7509546/')
    imgs.sort(key=lambda I: I.id)
    random.seed(0)
    random.shuffle(imgs)
    outputdir='./dna-images/gnf/'
    maybe_mkdir(outputdir)
    for i,img in enumerate(imgs[:50]):
        dna=img.get('dna')
        imsave('%s/dna-%s.png' % (outputdir,i), as_colourimg(dna))

def get_ksr():
    imgs=pyslic.image.io.read_ksr_dir('raw-data/080518MFJLX_CC1KSR/')
    F=pyslic.preprocess.preprocess_collection(imgs,pyslic.preprocess.FixIlluminationHVRadialGradient('dna'))
    imgs.sort(key=lambda x: x.id)
    L=100
    idx=0
    outputdir='dna-images/ksr'
    maybe_mkdir(outputdir)
    for img in imgs:
        with pyslic.image.loadedimage(img):
            F.process(img)
            dna=img.get('dna')
            if (dna > L*3).sum() > 100:
                imsave('%s/dna-%s.png' % (outputdir,idx), dna)
                idx += 1
                if idx == 50: break

def get_ic100():
    imgs=pyslic.image.io.read_ic100dir('raw-data/080328MFLPC_BV1/')
    wells=['C2','B2'] # These are two control wells: more cells.
    selected=[img for img in imgs if img.label in wells]
    def imgkey(I):
        w,c=I.id
        idx=(wells.index(w) if w in wells else len(wells))
        return idx,c
        if w in wells:
            return wells.index(w),c
        return len(wells),c

    selected.sort(key=imgkey)
    outputdir='dna-images/ic100'
    maybe_mkdir(outputdir)
    for idx,img in enumerate(selected[:50]):
        imsave('%s/dna-%s.png' % (outputdir,idx),as_colourimg(img.get('dna')))

def main(arg):
    if arg == 'gnf':
        get_gnf()
    elif arg == 'ic100':
        get_ic100()
    elif arg == 'ksr':
        get_ksr()
    else:
        print "Uknown collection '%s'" % arg
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg=sys.argv[1]
        main(arg)
    else:
        main('gnf')
        main('ic100')
        main('ksr')

