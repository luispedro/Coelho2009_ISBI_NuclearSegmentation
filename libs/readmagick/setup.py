# -*- coding: utf-8 -*-
# Copyright (C) 2008  Murphy Lab
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

import subprocess
from numpy.distutils.core import setup, Extension

def popen3(cmd):
    p = subprocess.Popen(cmd, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    return p.stdout, p.stdin, p.stderr

def readmagick_args(verbose=True):
    output,input,error = popen3('pkg-config ImageMagick++ --libs --cflags')
    errors = error.read()
    if errors:
        output,input,error = popen3('ImageMagick++-config --libs --cflags')
        errors += error.read()
    if errors:
        if verbose:
            print '''
Could not find ImageMagick++ headers using
pkg-config or ImageMagick++-config.

Error was: %s

readmagick will not be built.
''' % errors
        return None
    tokens = output.readline().split()
    input.close()
    output.close()
    args={ 'libraries'    : [t[2:] for t in tokens if t.startswith('-l')],
           'include_dirs' : [t[2:] for t in tokens if t.startswith('-I')],
           'library_dirs' : [t[2:] for t in tokens if t.startswith('-L')],
    }
    return args

long_description = '''ReadMagick

Read and write images using ImageMagick++.

Supports modern image formats such as JPEG2000.
'''
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: C++',
    'Topic :: Scientific/Engineering',
    ]


readmagick = Extension('readmagick.readmagick', sources = ['readmagick/readmagick.cpp'],  **readmagick_args())
setup(name = 'readmagick',
      version = '1.0.1',
      description = 'Read and write images using ImageMagick',
      long_description = long_description,
      classifiers = classifiers,
      author = 'Luis Pedro Coelho',
      author_email = 'lpc@mcu.edu',
      license = 'GPL',
      ext_modules = [readmagick]
      )

