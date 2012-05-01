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

from __future__ import with_statement, division
import numpy
import numpy as np
from scipy import ndimage
from glob import glob
import pymorph
from jug.task import Task, TaskGenerator
import pyslic
from pyslic.segmentation import *
from pyslic.image import loadedimage
from scipy import ndimage             
from images import *
from compare import *
from watershed import *
from roysam import compute_roysams, compute_roysams_mean, filter_small_nuclei

thresh_segment = TaskGenerator(pyslic.segmentation.threshold_segment)

@TaskGenerator
def segment_watershed_rc(img,mode='direct'):
    return segment_watershed(img,mode,'rc')

@TaskGenerator
def segment_watershed_mean(img,mode='direct'):
    return segment_watershed(img,mode,'mean')

@TaskGenerator
def active_mask(img):
    with loadedimage(img):
        return pyslic.segmentation.active_masks_dna(img.get('dna'),R=0)

@TaskGenerator
def active_mask2(img):
    with loadedimage(img):
        dna = img.get('dna')
        H = np.histogram(dna.ravel(),np.arange(257))[0]
        return pyslic.segmentation.active_masks(dna,3,1,{3: [8.,4.,2.], 2 : [8.,4.,2.], 1: [2.]},256,1.2,.5,H.argmax()+3)


refs = ic100_ref + gnf_ref

#ic100_ref_full = [extend_R(r) for r in ic100_ref]
#gnf_ref_full = [extend_R(r) for r in gnf_ref]
#refs_full = ic100_ref_full + gnf_ref_full

otsu = [thresh_segment(img,'otsu') for img in ic100_imgs + gnf_imgs]
mean_t = [thresh_segment(img,'mean') for img in ic100_imgs + gnf_imgs]
rc_t = [thresh_segment(img,'rc') for img in ic100_imgs + gnf_imgs]
#water_direct_raw = [segment_watershed(img,'direct',thresholding=None,min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
#water_direct = [segment_watershed(img,'direct',thresholding='otsu',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
#water_gradient = [segment_watershed(img,'gradient',thresholding='otsu',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
#water_direct_rc = [segment_watershed(img,'direct',thresholding='murphy_rc',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
#water_gradient_rc = [segment_watershed(img,'gradient',thresholding='murphy_rc',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
water_direct_mean = [segment_watershed(img,'direct',thresholding='mean',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
water_gradient_mean = [segment_watershed(img,'gradient',thresholding='mean',min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
#water_gradient_raw = [segment_watershed(img,'gradient',thresholding=None,min_obj_size=2500) for img in ic100_imgs + gnf_imgs]
active_masks = [active_mask(img) for img in ic100_imgs + gnf_imgs]
active_masks_filtered = [filter_small_nuclei(img) for img in active_masks]
#active_masks2 = [active_mask2(img) for img in ic100_imgs + gnf_imgs]
#roysams = compute_roysams(ic100_imgs,gnf_imgs)
roysams_mean = compute_roysams_mean(ic100_imgs,gnf_imgs)
roysams_mean_filtered = [filter_small_nuclei(img) for img in roysams_mean]

def _compare(name,segs,refs):
    compare(refs,ic100_ref,name,segs)

_compare('otsu',otsu,refs)
_compare('mean_t',mean_t,refs)
_compare('rc_t',rc_t,refs)
#_compare('watershed:direct',water_direct,refs)
#_compare('watershed:gradient',water_gradient,refs)
#_compare('watershed:direct_rc',water_direct_rc,refs)
#_compare('watershed:gradient_rc',water_gradient_rc,refs)
_compare('watershed:direct_mean',water_direct_mean,refs)
_compare('watershed:gradient_mean',water_gradient_mean,refs)
#_compare('watershed:direct_raw',water_direct_raw,refs)
#_compare('watershed:gradient_raw',water_gradient_raw,refs)
#_compare('watershed:direct:full',water_direct,refs_full)
#_compare('watershed:gradient:full',water_gradient,refs_full)
#_compare('watershed:direct_raw:full',water_direct_raw,refs_full)
#_compare('watershed:gradient_raw:full',water_gradient_raw,refs_full)
#_compare('active_masks',active_masks,refs)
_compare('active_masks:filtered',active_masks_filtered,refs)
#_compare('active_masks2',active_masks2,refs)
#_compare('roysam',roysams,refs)
_compare('roysam_mean',roysams_mean,refs)
#_compare('roysams_mean_filter',roysams_mean_filtered,refs)
_compare('roysams_mean_filter_no_AS',roysams_mean_filtered[5:],refs[5:])


aabid_refs = ic100_ref[:5] + gnf_ref[:5]
aabids = [Task(load_aabid,'ic100',i) for i in xrange(5)] +\
         [Task(load_aabid,'gnf',i) for i in xrange(5)]
compare(aabid_refs,ic100_ref[:5],'AS',aabids)


# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
