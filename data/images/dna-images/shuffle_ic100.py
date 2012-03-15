from glob import glob
import random
import os
inputdir = 'ic100'
outputdir = 'ic100-tbuck'

inputfiles=glob(inputdir + '/*.png')
random.seed(hash(outputdir))
random.shuffle(inputfiles)
os.mkdir(outputdir)
for i,f in enumerate(inputfiles):
    os.link(f,outputdir+('/dna-%s.png' %  i))
    
