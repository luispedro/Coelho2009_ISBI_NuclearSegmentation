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
from pylab import *
import numpy
import numpy as np
from images import *                           
from segment_base import *
def borders(img):
    res = np.zeros(img.shape,bool)
    res[:-1,:-1] = (img[:-1,:-1] != img[:-1,1:])
    res[1:,:] |= (img[1:,:] != img[:-1,:])
    res[:,1:] |= (img[:,1:] != img[:,:-1])
    return res

for idx,r,img in zip(xrange(48),gnf_ref,gnf_imgs):
    dna=img.get('dna')
    img.unload()
    rr = load_ref('gnf',gnf_idxs[idx])
    rr2 = r.result
    if np.all(rr == rr2): continue
    clf()
    imshow(pymorph.overlay(dna,borders(rr)))
    savefig('t/gnf_b%s.png' % idx)
    r.unload()
    
for idx,r,img in zip(xrange(48),ic100_ref,ic100_imgs):
    dna=img.get('dna')
    img.unload()
    rr = load_ref('ic100',ic100_idxs[idx])
    rr2 = r.result
    if np.all(rr == rr2): continue
    clf()
    imshow(pymorph.overlay(dna,borders(rr)))
    savefig('t/ic100_b%s.png' % idx)
    r.unload()
    
for idx,r,img in zip(xrange(5),aabids[5:10],gnf_imgs):
    dna=img.get('dna')
    img.unload()
    rr = load_ref('gnf',gnf_idxs[idx])
    rr2 = r.result
    if np.all(rr == rr2): continue
    clf()
    imshow(pymorph.overlay(dna,borders(rr)))
    savefig('t/aabid_gnf_b%s.png' % idx)
    r.unload()
    
for idx,r,img in zip(xrange(5),aabids[:5],ic100_imgs):
    dna=img.get('dna')
    img.unload()
    rr = load_ref('ic100',ic100_idxs[idx])
    rr2 = r.result
    if np.all(rr == rr2): continue
    clf()
    imshow(pymorph.overlay(dna,borders(rr)))
    savefig('t/aabid_ic100_b%s.png' % idx)
    r.unload()
    
