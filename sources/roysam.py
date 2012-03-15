# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009  Murphy Lab
# Carnegie Mellon University
# 
# Written by Luís Pedro Coelho <lpc@cmu.edu>
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
from __future__ import with_statement, division
from scipy import ndimage
import numpy as np
from jug.task import Task, TaskGenerator
import pyslic
from pyslic.image import loadedimage
import pyslic.segmentation.roysam
from images import load_aabid

@TaskGenerator
def compute_mu_sigma(col):
    aabids = [load_aabid(col,i) for i in xrange(5)]
    return pyslic.segmentation.roysam.train_classifier(aabids)

classif_ic100 = compute_mu_sigma('ic100')
classif_gnf = compute_mu_sigma('gnf')

@TaskGenerator
def roysam_seg(img, classif):
    with loadedimage(img):
        dna = img.get('dna')
        return pyslic.segmentation.roysam.greedy_roysam_merge(dna,classif)

def compute_roysams(ic100_imgs,gnf_imgs):
    roysams_ic100 = [roysam_seg(img,classif_ic100) for img in ic100_imgs]
    roysams_gnf = [roysam_seg(img,classif_gnf) for img in gnf_imgs]
    return roysams_ic100 + roysams_gnf

@TaskGenerator
def roysam_seg_mean(img,classif):
    with loadedimage(img):
        dna = img.get('dna')
        return pyslic.segmentation.roysam.greedy_roysam_merge(dna,classif,dna.mean())

def compute_roysams_mean(ic100_imgs,gnf_imgs):
    roysams_ic100 = [roysam_seg_mean(img,classif_ic100) for img in ic100_imgs]
    roysams_gnf = [roysam_seg_mean(img,classif_gnf) for img in gnf_imgs]
    return roysams_ic100 + roysams_gnf

@TaskGenerator
def filter_small_nuclei(img, min_size=2500):
    img = img.copy()
    N = img.max()
    obj = 1
    while obj <= N:
        if (img == obj).sum() < min_size:
            img[img == obj] = 0
            img[img > obj] -= 1
            N -= 1
        else:
            obj += 1
    return img
