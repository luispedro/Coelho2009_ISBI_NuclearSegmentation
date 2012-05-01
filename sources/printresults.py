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
import re
def printresults(name,inputfile):
    order = ('Jaccard','Hausdorff', 'Distances', 'Basics:Split', 'Basics:Merged', 'Basics:Added', 'Basics:Missing')
    pat = re.compile('([A-Z][A-Za-z:]+) ?\((IC100|GNF):.*\): ([0-9.]+)$')
    values = {}
    for line in file('results/'+inputfile):
        match = pat.match(line)
        if match is not None:
            dist,dataset,value = match.groups()
            values[dist,dataset] = float(value)
            
    print '%-24s &' % name,
    print '%s\\%%/%s\\%%    &' %(int(100*values['Rand','GNF']),int(100*values['Rand','IC100'])),
    for m in order:
        scale = (10 if m == 'Distances' else 1)
        print '%-16s&' % ('%.1f/%.1f'  % (scale*values[m,'GNF'],scale*values[m,'IC100'])),
    print r'\\'
printresults('AS Manual','AS.txt')
printresults('RC Threshold','rc_t.txt')
printresults('Otsu Threshold','otsu.txt')
printresults('Mean Threshold','mean_t.txt')
printresults('Watershed (direct)','watershed:direct_mean.txt')
printresults('Watershed (gradient)','watershed:gradient_mean.txt')
printresults('Active Masks','active_masks:filtered.txt')
printresults("Merging Algorithm",'roysams_mean_filter_no_AS.txt')

