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
from jug.task import Task, TaskGenerator
import numpy as np
from scipy import ndimage
import pyslic
import pymorph
from mahotas import morph

segment_watershed = TaskGenerator(pyslic.segmentation.watershed.watershed_segment)

@TaskGenerator
def extend_R(R):
    return morph.cwatershed(np.zeros(R.shape,np.uint8),R)

# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
