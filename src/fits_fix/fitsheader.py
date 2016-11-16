#!/usr/bin/python

import pyfits as pf
import numpy as np
import sys
import sys

infile = sys.argv[1]
print 'Processing FITS file :', infile

hdulist = pf.open(infile)
#print hdulist.info()
phdr=hdulist[0].header

for key in phdr.keys():
    print "Primary header key %s = %s"%(key,phdr[key])

for i in range(1,19) :
#for i in [18] :

    hdr=hdulist[i].header
    for key in hdr.keys():
        #key = 'V_OD1'#'V_BSS'
        print "Header %d key %s = %s"%(i,key,hdr[key])

hdulist.close()
