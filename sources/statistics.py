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
import numpy
from images import *
from scipy import ndimage
from glob import glob
import pymorph
from jug import task
from jug.task import TaskGenerator

@task.TaskGenerator
def compute_stats(original,ref_image):
    N = ref_image.max()
    sizes = numpy.array(ndimage.sum(ref_image > 0,ref_image,numpy.arange(N)))
    brightness = []
    for obj in xrange(1,N+1):
        brightness.append( ref_image[ref_image==obj].mean() )
    brightness = numpy.array(brightness)
    return N,sizes,brightness

stats_ic100 = [compute_stats(orig,ref) for orig,ref in zip(ic100_imgs,ic100_ref)]
stats_gnf   = [compute_stats(orig,ref) for orig,ref in zip(gnf_imgs,gnf_ref)]

@task.TaskGenerator(print_result=True)
def format_counts(counts):
    counts = numpy.array(counts)
    return \
'''\
Total Nr Cells:    %s
Mean Nr Cells:     %s
Min Nr Cells:      %s
Max Nr Cells:      %s
StdDev Nr Cells:   %s
''' % (counts.sum(),counts.mean(),counts.min(),counts.max(),counts.std())

@task.TaskGenerator
def extract_counts(stats):
    return stats[0]

counts_ic100 = format_counts([extract_counts(s) for s in stats_ic100])
counts_gnf = format_counts([extract_counts(s) for s in stats_gnf])

@task.TaskGenerator(print_result=True)
def sum_counts(stats):
    return sum(s[0] for s in stats)

total_ic100 = sum_counts(stats_ic100)
total_gnf = sum_counts(stats_gnf)

@TaskGenerator
def percent_cover(stats,pixels):
    _,sizes,_ = stats
    return (sum(sizes)-max(sizes))/pixels
covers_ic100=[percent_cover(s,1344*1024) for s in stats_ic100]
covers_gnf = [percent_cover(s,1349*1030) for s in stats_gnf]

