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

from mahotas import fullhistogram
from jug.task import TaskGenerator
import numpy as np
from mahotas.bbox import bbox
from scipy import ndimage
import pymorph

@TaskGenerator
def itk_comparison(labeled,reference):
    import SegmentationValidation
    import itk
    image_type = itk.Image[itk.UC,2]
    itk_py_converter = itk.PyBuffer[image_type]
    segmentation=SegmentationValidation.SimilarityIndexImageFilter[image_type,image_type].New()
    L_itk = itk_py_converter.GetImageFromArray(labeled)
    Ref_itk = itk_py_converter.GetImageFromArray(reference)
    segmentation.SetInput1(L_itk.GetPointer())
    segmentation.SetInput2(Ref_itk.GetPointer())
    A=segmentation.GetOutput()
    A_=itk_py_converter.GetArrayFromImage(A)
    return segmentation.GetSimilarityIndex()

@TaskGenerator
def basic_compare(segmented,ref):
    joint = np.histogram2d(ref.ravel(),segmented.ravel(),np.arange(max(ref.max(),segmented.max())+2))[0]
    assignments = joint.argmax(0)[:segmented.max() + 1]
    revassignments = joint.argmax(1)[:ref.max()+1]

    added = (assignments[1:] == 0).sum()
    missing = (revassignments[1:] == 0).sum()
    merged = (np.histogram(revassignments,np.arange(revassignments.max()+1))[0][2:] > 1).sum()
    split = (np.histogram(assignments,np.arange(assignments.max()+1))[0] > 1).sum()

    return added, missing, merged, split

@TaskGenerator
def rand_index(abcd):
    a,b,c,d = abcd
    return (a+d)/(a+b+c+d)

@TaskGenerator
def jaccard_index(abcd):
    a,b,c,d = abcd
    return (a+d)/(b+c+d)

@TaskGenerator
def compute_abcd(seg,ref):
    '''
    a,b,c,d = compute_abcd(segmented,reference)

    Compute a,b,c,d
    '''
    from scipy.misc import comb
    seg_flat = seg.ravel()
    ref_flat = ref.ravel()
    n = ref_flat.size
    A,_,_ = np.histogram2d(ref_flat,seg_flat,np.arange(max(ref_flat.max()+2,seg_flat.max()+2)))
    A_0 = A.sum(0)
    A_1 = A.sum(1)

    a=comb(A.ravel(),2).sum()
    b=comb(A_0.ravel(),2).sum()-a
    c=comb(A_1.ravel(),2).sum()-a
    d=comb(n,2)-a-b-c
    return a,b,c,d


def slow_rand(segmented,ref):
    from scipy import weave
    ref_flat = ref.ravel()
    seg_flat = segmented.ravel()
    n=ref_flat.size
    code='''
    long long int agree = 0;
    for (int i = 0 ; i != n; ++i) {
        for (int j = i + 1; j != n; ++j) {
            agree += ( (ref_flat(i) == ref_flat(j)) && (seg_flat(i) == seg_flat(j)) ) || ( (ref_flat(i) != ref_flat(j)) && (seg_flat(i) != seg_flat(j)) );
        }
    }
    return_val = double(agree);
    '''
    return weave.inline(code,['ref_flat','seg_flat','n'],type_converters=converters.blitz)


@TaskGenerator
def dist_hausdorff_compare(segmented, ref):
    joint = np.histogram2d(ref.ravel(),segmented.ravel(),np.arange(max(ref.max(),segmented.max())+2))[0]
    assignments = joint.argmax(0)[:segmented.max() + 1]                                                 
    #revassignments = joint.argmax(1)[:ref.max()+1]                                                      
    values = []
    hausdorff = []
    for i in xrange(1,int(segmented.max()+1)):
        if assignments[i] == 0:
            values += ['bg']
            continue
        min1,max1,min2,max2 = bbox( (ref==assignments[i]) | (segmented == i) )
        segc = (segmented[min1:max1,min2:max2] == i)
        refc = (ref[min1:max1,min2:max2] == assignments[i])
        dref = np.maximum(ndimage.distance_transform_edt(refc),ndimage.distance_transform_edt(~refc))
        values.append(dref[segc != refc].sum()/float(dref[segc|refc].sum()))
        hausdorff.append( (dref*(segc!=refc)).max() )
    return values, hausdorff


@TaskGenerator
def print_results(refs,ic100_ref,name,rands,jaccards,distances,basics):
    basics_ic100 = np.mean([basics[i] for i in xrange(len(ic100_ref))],0) 
    basics_gnf = np.mean([basics[i] for i in xrange(len(ic100_ref),len(refs))],0)
    def _g(d,deff):
        ds = []
        for dd in d:
            if dd == 'bg':
                ds.append(1)
            else:
                ds.append(dd)
        if not ds:
            return deff
        return np.mean(ds) 
    dists = np.array([_g(d[0],1.) for d in distances])
    haus = np.array([_g(d[1],128.) for d in distances])
    try:
        from os import mkdir
        mkdir('results')
    except:
        pass
    outf = file('results/%s.txt' % name,'w')
    print >>outf, 'Rand (IC100:%s):' % name, np.mean([rands[i] for i in xrange(len(ic100_ref))]) 
    print >>outf, 'Rand (GNF:%s):' % name, np.mean([rands[i] for i in xrange(len(ic100_ref),len(refs))]) 
    print >>outf
    print >>outf, 'Jaccard (IC100:%s):' %name, np.mean([jaccards[i] for i in xrange(len(ic100_ref))]) 
    print >>outf, 'Jaccard (GNF:%s):' %name , np.mean([jaccards[i] for i in xrange(len(ic100_ref),len(refs))]) 
    print >>outf
    print >>outf, 'Distances(IC100:%s):' %name, dists[:len(ic100_ref)].mean()
    print >>outf, 'Distances (GNF:%s):' %name, dists[len(ic100_ref):].mean()
    print >>outf
    print >>outf, 'Hausdorff (IC100:%s):' %name, haus[:len(ic100_ref)].mean()
    print >>outf, 'Hausdorff (GNF:%s):' %name, haus[len(ic100_ref):].mean()
    print >>outf
    print >>outf, 'Basics:Added (IC100:%s):' %name, basics_ic100[0]
    print >>outf, 'Basics:Added (GNF:%s):' %name , basics_gnf[0]
    print >>outf
    print >>outf, 'Basics:Missing (IC100:%s):' %name, basics_ic100[1]
    print >>outf, 'Basics:Missing (GNF:%s):' %name , basics_gnf[1]
    print >>outf
    print >>outf, 'Basics:Merged (IC100:%s):' %name, basics_ic100[2]
    print >>outf, 'Basics:Merged (GNF:%s):' %name , basics_gnf[2]
    print >>outf
    print >>outf, 'Basics:Split (IC100:%s):' %name, basics_ic100[3]
    print >>outf, 'Basics:Split (GNF:%s):' %name , basics_gnf[3]
    #print >>outf
    #print >>outf, 'ITKs (IC100:%s):' %name, np.mean([itks[i] for i in xrange(len(ic100_ref))]) 
    #print >>outf, 'ITKs (GNF:%s):' %name , np.mean([itks[i] for i in xrange(len(ic100_ref),len(refs))]) 
    outf.close()

def compare(refs,ic100_refs,name,segs):
    #itks = [itk_comparison(seg,ref) for seg,ref in zip (segs,refs)]
    basics = [basic_compare(seg,ref) for seg,ref in zip(segs,refs)]
    distances = [dist_hausdorff_compare(seg,ref) for seg,ref in zip(segs,refs)]
    abcds = [compute_abcd(seg,ref) for seg,ref in zip(segs,refs)]
    rand_indices = [rand_index(abcd) for abcd in abcds]
    jaccard_indices = [jaccard_index(abcd) for abcd in abcds]

    print_results(refs,ic100_refs,name,rand_indices,jaccard_indices,distances,basics)
