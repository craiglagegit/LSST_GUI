#!/usr/bin/python


import sys
sys.path.append('/sandbox/lsst/lsst/GUI')
import ucdavis2lsst

infile = sys.argv[1]

print 'Processing FITS file :', infile

ucdavis2lsst.fix(infile, "../UCDavis.cfg", "112-06", "target", "light", 1, 1.0, "R", 50.0, 1.0E-9, -194.2, -105.0, -105.0)
