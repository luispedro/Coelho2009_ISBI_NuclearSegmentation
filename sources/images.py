# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009  Murphy Lab
# Carnegie Mellon University
# 
# Written by Luis Pedro Coelho <luis@luispedro.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# For additional information visit http://murphylab.web.cmu.edu or
# send email to murphy@cmu.edu

from __future__ import division
from imread import imread
import tempfile
import os.path
from os import system
from glob import glob
from scipy import ndimage
from jug.task import Task

def readxcf(xcffilename):
    '''
    img = readxcf(xcf_filename)

    Returns a numpy array with the (flattened) XCF file.
    '''
    from os import unlink
    print 'readxcf(%s)' % xcffilename
    N=tempfile.NamedTemporaryFile(suffix='.png')
    system('xcf2png %s >%s' % (xcffilename,N.name))
    return imread(N.name)

def getborders(img):
    return (img[:,:,0] > img[:,:,1])


def _load_directory(pattern, stoplist):
    import pyslic
    imgs = []
    files = glob(pattern)
    def extract_number(path):
        assert path.endswith('.png'), 'extract_number: Cannot parse "%s"' % path
        path = path[:-len('.png')]
        path = path[ (path.rfind('-')+1): ]
        return int(path)
    files.sort(key=extract_number)
    for f in files:
        if extract_number(f) in stoplist: continue
        img = pyslic.Image()
        img.channels['dna'] = f
        imgs.append(img)
    return imgs

_ic100_stoplist = [25]
ic100_idxs = [i for i in xrange(50) if i not in _ic100_stoplist]
def load_ic100():
    '''imgs = load_ic100()'''
    return _load_directory('../data/images/dna-images/ic100/*.png',_ic100_stoplist)


_gnf_stoplist = [31,43]
gnf_idxs = [i for i in xrange(50) if i not in _gnf_stoplist]
def load_gnf():
    '''imgs = load_gnf()'''
    return _load_directory('../data/images/dna-images/gnf/*.png',_gnf_stoplist)

_min_obj_size = 32 
def load_ref(col,id):
    '''
    img = load_col_ref(id)

    id: either integer or string
    '''
    if type(id) == int:
        assert col in ('gnf','ic100')
        path = ('../data/images/segmented-lpc/%s/dna-%s.png' % (col,id))
        reader = imread
        if not os.path.exists(path):
            path = ('../data/images/segmented-lpc/%s/dna-%s.xcf' % (col,id))
            reader = readxcf
    B = getborders(reader(path))
    return _process_B(B)

def _process_B(B):
    L,N = ndimage.label(~B)
    bg = 0
    bg_size = (L==bg).sum()
    for i in xrange(1,N+1):
        i_size = (L == i).sum()
        if i_size > bg_size:
            bg_size = i_size
            bg = i
        if i_size < _min_obj_size:
            L[L==i] = 0 
    L[L==bg]=0
    L,_ = ndimage.label(L!=0)
    return L


def load_aabid(col,id):
    from readmagick import readimg
    id = ('../data/images/segmented-ashariff/%s/dna-%s.psd' % (col,id))
    I = readimg(id)
    B = (I[:,:,0] > I[:,:,1])
    return _process_B(B)

ic100_imgs = load_ic100()
gnf_imgs = load_gnf()

ic100_ref = [Task(load_ref,'ic100',i) for i in ic100_idxs]
gnf_ref = [Task(load_ref,'gnf',i) for i in gnf_idxs]
